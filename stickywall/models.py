from django.conf import settings
from django.db import models
from workspaces.models import Workspace

COLOR_CHOICES = [
    ("#FFFD75", "Yellow"), ("#FFA500", "Orange"), ("#FFC0CB", "Pink"),
    ("#ADFF2F", "Light green"), ("#98FB98", "Mint"), ("#FF69B4", "Hot pink"),
]


class Note(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="notes")
    text = models.TextField(blank=True)
    color = models.CharField(max_length=10, default="#FFFD75")
    rotate_deg = models.FloatField(default=0)
    pos_x = models.IntegerField(default=20)
    pos_y = models.IntegerField(default=20)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
