from django.conf import settings
from django.db import models

WS_ICON_COLORS = ["#5eead4", "#a78bfa", "#fb923c", "#4ade80", "#f472b6", "#60a5fa"]


class Workspace(models.Model):
    name = models.CharField(max_length=100)
    icon_color = models.CharField(max_length=10, default="#4ade80")
    icon_letter = models.CharField(max_length=2, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_workspaces")
    is_personal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.icon_letter:
            self.icon_letter = (self.name or "W")[0].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        return self.memberships.count()


class Membership(models.Model):
    ROLE_CHOICES = (("owner", "Owner"), ("admin", "Admin"), ("member", "Member"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships")
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="member")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "workspace")

    def __str__(self):
        return f"{self.user} @ {self.workspace} ({self.role})"


class Invite(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="invites")
    email = models.EmailField()
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)


class Team(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="teams")
    name = models.CharField(max_length=80)
    color = models.CharField(max_length=10, default="#60a5fa")
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="teams", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
