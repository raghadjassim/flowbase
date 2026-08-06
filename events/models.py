from django.conf import settings
from django.db import models
from workspaces.models import Workspace

COLOR_CHOICES = [("#4ade80", "Green"), ("#60a5fa", "Blue"), ("#fb923c", "Orange"), ("#f472b6", "Pink"), ("#a78bfa", "Purple")]


class Event(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="events")
    title = models.CharField(max_length=150)
    description = models.CharField(max_length=500, blank=True)
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    color = models.CharField(max_length=10, default="#4ade80")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_events")
    attendees = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="events", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "start_time"]

    def __str__(self):
        return self.title
