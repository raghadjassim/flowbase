from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    path("", views.list_view, name="list"),
    path("mark-all-read/", views.mark_all_read, name="mark_all_read"),
    path("api/unread/", views.api_unread, name="api_unread"),
]
