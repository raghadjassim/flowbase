import json
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import Project, Column, Task, Comment
from notifications.models import Notification

User = get_user_model()


@login_required
def project_list(request):
    projects = Project.objects.filter(workspace=request.workspace)
    return render(request, "boards/project_list.html", {"projects": projects})


@login_required
@require_POST
def create_project(request):
    name = request.POST.get("name", "مشروع جديد")
    project = Project.objects.create(workspace=request.workspace, name=name, created_by=request.user)
    project.ensure_default_columns()
    return redirect("boards:project_detail", pk=project.pk)


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk, workspace=request.workspace)
    project.ensure_default_columns()
    columns = project.columns.prefetch_related("tasks__assignees")
    members = User.objects.filter(memberships__workspace=request.workspace)
    teams = request.workspace.teams.all()
    return render(request, "boards/project_detail.html", {
        "project": project, "columns": columns, "members": members, "teams": teams,
    })


@login_required
@require_POST
def create_task(request, project_id):
    project = get_object_or_404(Project, pk=project_id, workspace=request.workspace)
    data = json.loads(request.body or "{}")
    column = get_object_or_404(Column, pk=data.get("column_id"), project=project)
    task = Task.objects.create(
        project=project, column=column,
        title=data.get("title", "مهمة جديدة"),
        description=data.get("description", ""),
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
    return JsonResponse({
        "ok": True, "id": task.id, "title": task.title, "priority": task.priority,
        "due_date": task.due_date.strftime("%Y-%m-%d") if task.due_date else "",
        "assignees": [{"id": u.id, "initial": u.initial, "color": u.avatar_color, "name": u.get_full_name() or u.username} for u in task.assignees.all()],
    })


@login_required
@require_POST
def move_task(request, pk):
    task = get_object_or_404(Task, pk=pk, project__workspace=request.workspace)
    data = json.loads(request.body or "{}")
    column = get_object_or_404(Column, pk=data.get("column_id"), project=task.project)
    task.column = column
    task.order = data.get("order", 0)
    if column.name.lower() == "completed" and not task.completed_at:
        task.completed_at = timezone.now()
    task.save()
    return JsonResponse({"ok": True})


@login_required
@require_POST
def update_task(request, pk):
    task = get_object_or_404(Task, pk=pk, project__workspace=request.workspace)
    data = json.loads(request.body or "{}")
    if "title" in data:
        task.title = data["title"]
    if "description" in data:
        task.description = data["description"]
    if "priority" in data:
        task.priority = data["priority"]
    if "due_date" in data:
        task.due_date = data["due_date"] or None
    task.save()
    if "assignees" in data:
        new_ids = set(int(i) for i in data["assignees"])
        old_ids = set(task.assignees.values_list("id", flat=True))
        task.assignees.set(new_ids)
        for uid in (new_ids - old_ids):
            u = User.objects.get(id=uid)
            if u != request.user:
                Notification.push(u, f"You were assigned to: {task.title}", type="assignment",
                                   body=task.project.name, link=f"/boards/{task.project.id}/")
    return JsonResponse({"ok": True})


@login_required
@require_POST
def delete_task(request, pk):
    Task.objects.filter(pk=pk, project__workspace=request.workspace).delete()
    return JsonResponse({"ok": True})


@login_required
def my_tasks(request):
    tasks = Task.objects.filter(project__workspace=request.workspace, assignees=request.user).select_related("project", "column")
    return render(request, "boards/my_tasks.html", {"tasks": tasks})


@login_required
def activity_view(request):
    tasks = Task.objects.filter(project__workspace=request.workspace).order_by("-created_at")[:30]
    return render(request, "boards/activity.html", {"tasks": tasks})
