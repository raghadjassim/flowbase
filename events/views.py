import json
from datetime import date, datetime
from calendar import Calendar, month_name

from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .models import Event
from notifications.models import Notification

User = get_user_model()


@login_required
def calendar_view(request):
    today = date.today()
    year = int(request.GET.get("y", today.year))
    month = int(request.GET.get("m", today.month))

    cal = Calendar(firstweekday=5)  # Saturday first (common in Iraq/MENA)
    weeks = cal.monthdatescalendar(year, month)

    events = Event.objects.filter(workspace=request.workspace, date__year=year, date__month=month)
    events_by_day = {}
    for e in events:
        events_by_day.setdefault(e.date.day, []).append(e)

    days = []
    for week in weeks:
        row = []
        for d in week:
            row.append({
                "date": d,
                "in_month": d.month == month,
                "is_today": d == today,
                "events": events_by_day.get(d.day, []) if d.month == month else [],
            })
        days.append(row)

    prev_month = (month - 1) or 12
    prev_year = year - 1 if month == 1 else year
    next_month = (month % 12) + 1
    next_year = year + 1 if month == 12 else year

    members = User.objects.filter(memberships__workspace=request.workspace)
    upcoming = Event.objects.filter(workspace=request.workspace, date__gte=today).order_by("date", "start_time")[:6]

    context = {
        "weeks": days,
        "month_label": f"{month_name[month]} {year}",
        "prev_month": prev_month, "prev_year": prev_year,
        "next_month": next_month, "next_year": next_year,
        "cur_year": year, "cur_month": month,
        "members": members,
        "upcoming": upcoming,
        "color_choices": Event._meta.get_field("color").choices,
    }
    return render(request, "events/calendar.html", context)


@login_required
@require_POST
def create_event(request):
    data = json.loads(request.body or "{}")
    e = Event.objects.create(
        workspace=request.workspace,
        title=data.get("title", "بدون عنوان"),
        description=data.get("description", ""),
        date=data.get("date"),
        start_time=data.get("start_time") or None,
        end_time=data.get("end_time") or None,
        color=data.get("color", "#4ade80"),
        created_by=request.user,
    )
    attendee_ids = data.get("attendees", [])
    if attendee_ids:
        e.attendees.set(attendee_ids)
        for u in e.attendees.exclude(id=request.user.id):
            Notification.push(u, f"Meeting invite: {e.title}", type="event",
                               body=f"On {e.date}", link="/calendar/")
    return JsonResponse({"ok": True, "id": e.id})


@login_required
@require_POST
def delete_event(request, pk):
    Event.objects.filter(pk=pk, workspace=request.workspace).delete()
    return JsonResponse({"ok": True})


@login_required
def api_reminders(request):
    """Returns events happening today for the toast/reminder system."""
    today = date.today()
    events = Event.objects.filter(workspace=request.workspace, date=today, attendees=request.user)
    items = [{"title": e.title, "time": e.start_time.strftime("%H:%M") if e.start_time else ""} for e in events]
    return JsonResponse({"items": items})
