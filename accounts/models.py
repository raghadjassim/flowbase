from django.contrib.auth.models import AbstractUser
from django.db import models
import random

AVATAR_COLORS = ["#5eead4", "#a78bfa", "#fb923c", "#4ade80", "#f472b6", "#60a5fa", "#facc15"]


class User(AbstractUser):
    THEME_CHOICES = (("dark", "Dark"), ("light", "Light"))
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default="dark")
    avatar_color = models.CharField(max_length=10, default="#5eead4")
    job_title = models.CharField(max_length=100, blank=True)
    bio = models.CharField(max_length=255, blank=True)
    email_reminders = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.avatar_color:
            self.avatar_color = random.choice(AVATAR_COLORS)
        super().save(*args, **kwargs)

    @property
    def initial(self):
        return (self.first_name or self.username or "?")[0].upper()
