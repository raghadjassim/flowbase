from django.conf import settings
from django.db import models
from workspaces.models import Workspace, Team

PROJECT_COLORS = ["#a78bfa", "#fb923c", "#4ade80", "#f472b6", "#60a5fa", "#facc15", "#5eead4"]


class Project(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="projects")
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)
    color = models.CharField(max_length=10, default="#a78bfa")
    icon_letter = models.CharField(max_length=2, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.icon_letter:
            self.icon_letter = (self.name or "P")[0].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def ensure_default_columns(self):
        if not self.columns.exists():
            for i, name in enumerate(["To do", "In progress", "Completed"]):
                Column.objects.create(project=self, name=name, order=i)

    @staticmethod
    def get_or_create_default(workspace, user):
        """Every workspace always has at least one project so tasks can be
        added right away, without forcing the user to create a project first."""
        project = Project.objects.filter(workspace=workspace).order_by("created_at").first()
        if not project:
            project = Project.objects.create(workspace=workspace, name="General", created_by=user, color="#5be59a")
        project.ensure_default_columns()
        return project

    @property
    def progress_percent(self):
        total = Task.objects.filter(column__project=self).count()
        if not total:
            return 0
        done = Task.objects.filter(column__project=self, column__name__iexact="Completed").count()
        return int(done * 100 / total)


class Column(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="columns")
    name = models.CharField(max_length=50)
    order = models.PositiveIntegerField(default=0)
    color = models.CharField(max_length=10, default="#9aa5b1")

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.project.name} / {self.name}"


class Task(models.Model):
    PRIORITY_CHOICES = (("low", "Low"), ("medium", "Medium"), ("high", "High"))
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    column = models.ForeignKey(Column, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")
    due_date = models.DateField(null=True, blank=True)
    assignees = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="assigned_tasks", blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_tasks")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
