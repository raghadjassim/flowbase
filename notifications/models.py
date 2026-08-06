from django.conf import settings
from django.db import models

TYPE_CHOICES = (
    ("assignment", "Task assignment"),
    ("event", "Meeting invite"),
    ("reminder", "Reminder"),
    ("workspace", "Workspace"),
    ("comment", "Comment"),
)


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="reminder")
    title = models.CharField(max_length=150)
    body = models.CharField(max_length=255, blank=True)
    link = models.CharField(max_length=255, blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @staticmethod
    def push(user, title, type="reminder", body="", link=""):
        return Notification.objects.create(user=user, title=title, body=body, type=type, link=link)
