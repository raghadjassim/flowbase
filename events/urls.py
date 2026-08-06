from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    path("", views.calendar_view, name="calendar"),
    path("api/create/", views.create_event, name="create_event"),
    path("api/<int:pk>/delete/", views.delete_event, name="delete_event"),
    path("api/reminders/", views.api_reminders, name="api_reminders"),
]
