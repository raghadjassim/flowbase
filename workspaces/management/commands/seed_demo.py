from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from workspaces.models import Workspace, Membership, Team
from boards.models import Project, Column, Task
from stickywall.models import Note
from events.models import Event
from notifications.models import Notification
from datetime import date, timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = "Seed demo data for Flowbase (a test user + workspace + sample content)"

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(username="test", defaults={
            "first_name": "Test", "email": "test@flowbase.dev",
        })
        if created:
            user.set_password("test1234")
            user.save()
            self.stdout.write(self.style.SUCCESS("Created user 'test' / password 'test1234'"))

        ws, _ = Workspace.objects.get_or_create(name="Q3 Product Launch", owner=user, defaults={"icon_color": "#a78bfa"})
        Membership.objects.get_or_create(user=user, workspace=ws, defaults={"role": "owner"})

        colleague, cc = User.objects.get_or_create(username="sara", defaults={"first_name": "Sara", "email": "sara@flowbase.dev"})
        if cc:
            colleague.set_password("test1234")
            colleague.save()
        Membership.objects.get_or_create(user=colleague, workspace=ws, defaults={"role": "member"})

        team, _ = Team.objects.get_or_create(workspace=ws, name="Dev Team", defaults={"color": "#60a5fa"})
        team.members.add(user, colleague)

        project, pc = Project.objects.get_or_create(workspace=ws, name="Mobile App", defaults={"created_by": user, "color": "#a78bfa"})
        project.ensure_default_columns()
        if pc:
            todo, inprog, done = project.columns.order_by("order")
            t1 = Task.objects.create(project=project, column=todo, title="Design the login screen", priority="high", created_by=user, due_date=date.today() + timedelta(days=2))
            t1.assignees.add(user)
            t2 = Task.objects.create(project=project, column=inprog, title="Wire up auth API", priority="medium", created_by=user)
            t2.assignees.add(colleague)
            Task.objects.create(project=project, column=done, title="Set up project environment", priority="low", created_by=user, completed_at="2026-08-01")

            Note.objects.create(workspace=ws, created_by=user, text="Idea: add offline mode", color="#FFFD75", pos_x=40, pos_y=40, rotate_deg=-3)
            Note.objects.create(workspace=ws, created_by=user, text="Reminder: review meeting Thursday", color="#98FB98", pos_x=340, pos_y=80, rotate_deg=4)

            Event.objects.create(workspace=ws, title="Weekly team sync", date=date.today() + timedelta(days=1), start_time="10:00", color="#4ade80", created_by=user)
            Notification.push(user, "You were added to a workspace", type="workspace")

        self.stdout.write(self.style.SUCCESS("Demo data ready."))
