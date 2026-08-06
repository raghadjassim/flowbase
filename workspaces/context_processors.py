from .models import Membership
from notifications.models import Notification


def workspace_context(request):
    ctx = {}
    if getattr(request, "user", None) and request.user.is_authenticated:
        ctx["current_workspace"] = getattr(request, "workspace", None)
        ctx["my_workspaces"] = Membership.objects.filter(user=request.user).select_related("workspace")
        ctx["unread_notifications_count"] = Notification.objects.filter(user=request.user, read=False).count()
        ctx["recent_notifications"] = Notification.objects.filter(user=request.user).order_by("-created_at")[:6]
    return ctx
