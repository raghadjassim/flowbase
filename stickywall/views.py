import json, random
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Note


@login_required
def focus_wall(request):
    notes = Note.objects.filter(workspace=request.workspace)
    return render(request, "stickywall/focus_wall.html", {"notes": notes})


@login_required
@require_POST
def create_note(request):
    rotate = round(random.uniform(-5, 5), 2)
    note = Note.objects.create(
        workspace=request.workspace, created_by=request.user,
        rotate_deg=rotate, pos_x=random.randint(20, 200), pos_y=random.randint(20, 120),
    )
    return JsonResponse({"ok": True, "id": note.id, "rotate": rotate, "x": note.pos_x, "y": note.pos_y, "color": note.color})


@login_required
@require_POST
def update_note(request, pk):
    note = get_object_or_404(Note, pk=pk, workspace=request.workspace)
    data = json.loads(request.body or "{}")
    if "text" in data:
        note.text = data["text"]
    if "color" in data:
        note.color = data["color"]
    if "x" in data:
        note.pos_x = int(data["x"])
    if "y" in data:
        note.pos_y = int(data["y"])
    note.save()
    return JsonResponse({"ok": True})


@login_required
@require_POST
def delete_note(request, pk):
    Note.objects.filter(pk=pk, workspace=request.workspace).delete()
    return JsonResponse({"ok": True})
