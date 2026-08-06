from django.contrib import admin
from .models import Project, Column, Task, Comment
admin.site.register(Project)
admin.site.register(Column)
admin.site.register(Task)
admin.site.register(Comment)
