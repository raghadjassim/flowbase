import os
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = (
        "Idempotent bootstrap for deploy environments without shell access "
        "(e.g. Render free tier). Creates/updates an admin superuser from "
        "ADMIN_USERNAME / ADMIN_PASSWORD / ADMIN_EMAIL env vars, then runs "
        "seed_demo. Safe to run on every build."
    )

    def handle(self, *args, **options):
        username = os.environ.get("ADMIN_USERNAME")
        password = os.environ.get("ADMIN_PASSWORD")
        email = os.environ.get("ADMIN_EMAIL", "")

        if username and password:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": email, "is_staff": True, "is_superuser": True},
            )
            user.email = email or user.email
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created admin superuser '{username}'."))
            else:
                self.stdout.write(self.style.SUCCESS(f"Updated existing superuser '{username}'."))
        else:
            self.stdout.write(self.style.WARNING(
                "ADMIN_USERNAME / ADMIN_PASSWORD not set — skipping superuser creation."
            ))

        if os.environ.get("SEED_DEMO_DATA", "true").lower() == "true":
            call_command("seed_demo")
