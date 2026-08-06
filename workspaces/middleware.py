from .models import Workspace, Membership


class CurrentWorkspaceMiddleware:
    """Attaches request.workspace = the currently selected workspace for logged-in users."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.workspace = None
        if request.user.is_authenticated:
            ws_id = request.session.get("current_workspace_id")
            membership_qs = Membership.objects.filter(user=request.user).select_related("workspace")
            membership = None
            if ws_id:
                membership = membership_qs.filter(workspace_id=ws_id).first()
            if not membership:
                membership = membership_qs.first()
                if membership:
                    request.session["current_workspace_id"] = membership.workspace_id
            if membership:
                request.workspace = membership.workspace
                request.membership = membership
        response = self.get_response(request)
        return response
