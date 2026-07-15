import datetime

from django.utils import timezone
from icalendar import Calendar
from icalendar import Event as ICalEvent

from .models import Event, Semester, TeachingAssignment

WEEKDAY_ICAL = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]


def _next_occurrence(start_date: datetime.date, day_of_week: int) -> datetime.date:
    days_ahead = (day_of_week - start_date.weekday()) % 7
    return start_date + datetime.timedelta(days=days_ahead)


def build_ics_calendar() -> Calendar:
    """Build an iCalendar feed of the active semester's teaching plus future events."""
    cal = Calendar()
    cal.add("prodid", "-//LecturerHub//Schedule//EN")
    cal.add("version", "2.0")

    semester = Semester.objects.filter(is_active=True).first()
    if semester:
        assignments = TeachingAssignment.objects.filter(semester=semester).select_related("course")
        for assignment in assignments:
            first_date = _next_occurrence(semester.start_date, assignment.day_of_week)
            dtstart = datetime.datetime.combine(first_date, assignment.start_time)
            dtend = datetime.datetime.combine(first_date, assignment.end_time)

            ical_event = ICalEvent()
            ical_event.add(
                "summary", f"{assignment.course.code} {assignment.class_label}".strip()
            )
            ical_event.add("dtstart", dtstart)
            ical_event.add("dtend", dtend)
            ical_event.add("location", assignment.room)
            ical_event.add(
                "rrule",
                {
                    "freq": "weekly",
                    "byday": WEEKDAY_ICAL[assignment.day_of_week],
                    "until": semester.end_date,
                },
            )
            ical_event.add("uid", f"assignment-{assignment.pk}@lecturerhub")
            cal.add_component(ical_event)

    for event in Event.objects.filter(start_datetime__gte=timezone.now()):
        ical_event = ICalEvent()
        ical_event.add("summary", event.title)
        ical_event.add("dtstart", event.start_datetime)
        ical_event.add("dtend", event.end_datetime)
        ical_event.add("location", event.location)
        if event.notes:
            ical_event.add("description", event.notes)
        ical_event.add("uid", f"event-{event.pk}@lecturerhub")
        cal.add_component(ical_event)

    return cal
