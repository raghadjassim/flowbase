from django.urls import path
from . import views

app_name = "stickywall"

urlpatterns = [
    path("", views.focus_wall, name="focus_wall"),
    path("api/create/", views.create_note, name="create_note"),
    path("api/<int:pk>/update/", views.update_note, name="update_note"),
    path("api/<int:pk>/delete/", views.delete_note, name="delete_note"),
]
