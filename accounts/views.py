import json
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from .forms import SignupForm, LoginForm, ProfileForm
from workspaces.models import Workspace, Membership
from boards.models import Project


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("workspaces:overview")
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        ws = Workspace.objects.create(name=f"{user.first_name or user.username}'s Workspace", owner=user, is_personal=True)
        Membership.objects.create(user=user, workspace=ws, role="owner")
        Project.get_or_create_default(ws, user)
        request.session["current_workspace_id"] = ws.id
        messages.success(request, "Your account is ready! Welcome to Flowbase 🎉")
        return redirect("workspaces:overview")
    return render(request, "accounts/signup.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("workspaces:overview")
    form = LoginForm(request.POST or None)
    error = None
    if request.method == "POST" and form.is_valid():
        user = authenticate(request, username=form.cleaned_data["username"], password=form.cleaned_data["password"])
        if user is not None:
            login(request, user)
            first_ws = Membership.objects.filter(user=user).first()
            if first_ws:
                request.session["current_workspace_id"] = first_ws.workspace_id
            return redirect("workspaces:overview")
        error = "Incorrect username or password."
    return render(request, "accounts/login.html", {"form": form, "error": error})


@login_required
def logout_view(request):
    logout(request)
    return redirect("accounts:login")


@login_required
def settings_view(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Settings saved.")
        return redirect("accounts:settings")
    return render(request, "accounts/settings.html", {"form": form})


@login_required
@require_POST
def set_theme(request):
    data = json.loads(request.body or "{}")
    theme = data.get("theme")
    if theme in ("dark", "light"):
        request.user.theme = theme
        request.user.save(update_fields=["theme"])
        return JsonResponse({"ok": True, "theme": theme})
    return JsonResponse({"ok": False}, status=400)
