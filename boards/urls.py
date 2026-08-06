from django.urls import path
from . import views

app_name = "boards"

urlpatterns = [
    path("", views.project_list, name="project_list"),
    path("create/", views.create_project, name="create_project"),
    path("my-tasks/", views.my_tasks, name="my_tasks"),
    path("activity/", views.activity_view, name="activity"),
    path("<int:pk>/", views.project_detail, name="project_detail"),
    path("<int:project_id>/tasks/create/", views.create_task, name="create_task"),
    path("tasks/<int:pk>/move/", views.move_task, name="move_task"),
    path("tasks/<int:pk>/update/", views.update_task, name="update_task"),
    path("tasks/<int:pk>/delete/", views.delete_task, name="delete_task"),
]
