from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from .models import Notification


@login_required
def list_view(request):
    notes = Notification.objects.filter(user=request.user)
    Notification.objects.filter(user=request.user, read=False).update(read=True)
    return render(request, "notifications/list.html", {"notes": notes})


@login_required
@require_POST
def mark_all_read(request):
    Notification.objects.filter(user=request.user, read=False).update(read=True)
    return JsonResponse({"ok": True})


@login_required
def api_unread(request):
    notes = Notification.objects.filter(user=request.user).order_by("-created_at")[:8]
    data = [
        {
            "id": n.id, "title": n.title, "body": n.body, "link": n.link,
            "type": n.type, "read": n.read, "created_at": n.created_at.strftime("%H:%M %d/%m"),
        } for n in notes
    ]
    return JsonResponse({"count": Notification.objects.filter(user=request.user, read=False).count(), "items": data})
