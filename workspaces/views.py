import json
import random
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Workspace, Membership, Invite, Team, WS_ICON_COLORS
from boards.models import Project, Column, Task
from notifications.models import Notification

User = get_user_model()


@login_required
def overview(request):
    ws = request.workspace
    if not ws:
        return redirect("workspaces:create")

    # Every workspace always has at least one project ready, so a task can be
    # added straight from the dashboard without creating a project first.
    default_project = Project.get_or_create_default(ws, request.user)
    default_column = default_project.columns.order_by("order").first()

    my_open_tasks = Task.objects.filter(project__workspace=ws, assignees=request.user).exclude(column__name__iexact="Completed")
    in_progress = Task.objects.filter(project__workspace=ws, column__name__iexact="In progress")
    week_ago = timezone.now() - timedelta(days=7)
    completed_week = Task.objects.filter(project__workspace=ws, column__name__iexact="Completed", completed_at__gte=week_ago)

    priority_tasks = my_open_tasks.select_related("column", "project")[:6]
    projects = Project.objects.filter(workspace=ws)
    members = User.objects.filter(memberships__workspace=ws)

    context = {
        "my_open_tasks_count": my_open_tasks.count(),
        "my_open_due_today": my_open_tasks.filter(due_date=timezone.localdate()).count(),
        "in_progress_count": in_progress.count(),
        "projects_count": projects.count(),
        "completed_week_count": completed_week.count(),
        "priority_tasks": priority_tasks,
        "projects": projects,
        "default_project": default_project,
        "default_column": default_column,
        "members": members,
    }
    return render(request, "workspaces/overview.html", context)


@login_required
@require_POST
def quick_add_task(request):
    """Used by the 'New task' button on the dashboard — creates a task in the
    workspace's default project without requiring the user to open a project first."""
    ws = request.workspace
    data = json.loads(request.body or "{}")
    project = Project.get_or_create_default(ws, request.user)
    column = project.columns.order_by("order").first()
    task = Task.objects.create(
        project=project, column=column,
        title=data.get("title", "New task"),
        priority=data.get("priority", "medium"),
        due_date=data.get("due_date") or None,
        created_by=request.user,
    )
    assignee_ids = data.get("assignees", [])
    if assignee_ids:
        task.assignees.set(assignee_ids)
        for u in task.assignees.exclude(id=request.user.id):
            Notification.push(u, f"You were assigned to: {task.title}", type="assignment",
                               body=project.name, link=f"/boards/{project.id}/")
    return JsonResponse({"ok": True, "id": task.id, "project_id": project.id})


@login_required
def create_workspace(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip() or "New workspace"
        ws = Workspace.objects.create(name=name, owner=request.user, icon_color=random.choice(WS_ICON_COLORS))
        Membership.objects.create(user=request.user, workspace=ws, role="owner")
        Project.get_or_create_default(ws, request.user)
        request.session["current_workspace_id"] = ws.id
        messages.success(request, f'Workspace "{name}" created.')
        return redirect("workspaces:overview")
    return render(request, "workspaces/create.html")


@login_required
def switch_workspace(request, pk):
    membership = get_object_or_404(Membership, workspace_id=pk, user=request.user)
    request.session["current_workspace_id"] = membership.workspace_id
    return redirect("workspaces:overview")


@login_required
def invite_teammates(request):
    ws = request.workspace
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        if email:
            existing_user = User.objects.filter(email__iexact=email).first()
            if existing_user:
                Membership.objects.get_or_create(user=existing_user, workspace=ws, defaults={"role": "member"})
                Notification.push(existing_user, f"You were added to workspace {ws.name}", type="workspace", link="/")
                messages.success(request, f"{email} was added to the workspace directly.")
            else:
                Invite.objects.create(workspace=ws, email=email, invited_by=request.user)
                messages.success(request, f"Invite sent to {email}.")
        return redirect("workspaces:invite")
    members = Membership.objects.filter(workspace=ws).select_related("user")
    pending = Invite.objects.filter(workspace=ws, accepted=False)
    return render(request, "workspaces/invite.html", {"members": members, "pending": pending})


@login_required
def teams_view(request):
    ws = request.workspace
    if request.method == "POST":
        name = request.POST.get("name", "").strip() or "New team"
        team = Team.objects.create(workspace=ws, name=name, color=random.choice(WS_ICON_COLORS))
        team.members.add(request.user)
        return redirect("workspaces:teams")
    teams = Team.objects.filter(workspace=ws).prefetch_related("members")
    members = User.objects.filter(memberships__workspace=ws)
    return render(request, "workspaces/teams.html", {"teams": teams, "members": members})


@login_required
@require_POST
def team_toggle_member(request, pk, user_id):
    team = get_object_or_404(Team, pk=pk, workspace=request.workspace)
    user = get_object_or_404(User, pk=user_id)
    if team.members.filter(id=user.id).exists():
        team.members.remove(user)
        added = False
    else:
        team.members.add(user)
        added = True
        if user != request.user:
            Notification.push(user, f"You were added to team {team.name}", type="workspace")
    return JsonResponse({"ok": True, "added": added})


@login_required
@require_POST
def team_delete(request, pk):
    Team.objects.filter(pk=pk, workspace=request.workspace).delete()
    return JsonResponse({"ok": True})
