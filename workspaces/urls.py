from django.urls import path
from . import views

app_name = "workspaces"

urlpatterns = [
    path("", views.overview, name="overview"),
    path("api/quick-add-task/", views.quick_add_task, name="quick_add_task"),
    path("create/", views.create_workspace, name="create"),
    path("switch/<int:pk>/", views.switch_workspace, name="switch"),
    path("invite/", views.invite_teammates, name="invite"),
    path("teams/", views.teams_view, name="teams"),
    path("teams/<int:pk>/toggle/<int:user_id>/", views.team_toggle_member, name="team_toggle_member"),
    path("teams/<int:pk>/delete/", views.team_delete, name="team_delete"),
]
