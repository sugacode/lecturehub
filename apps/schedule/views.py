import calendar as calendar_module
import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.common.htmx import htmx_row_deleted, toast_header

from .forms import CourseForm, EventForm, SemesterForm, TeachingAssignmentForm
from .ics_export import build_ics_calendar
from .models import Course, Event, Semester, TeachingAssignment

WEEKDAY_LABELS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
CALENDAR_START_HOUR = 7
CALENDAR_END_HOUR = 21


class ToastFormMixin:
    success_message = "Saved."

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response


class HtmxDeleteView(LoginRequiredMixin, DeleteView):
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        label = str(self.object)
        self.object.delete()
        if request.headers.get("HX-Request"):
            return htmx_row_deleted(f'Deleted "{label}".')
        messages.success(request, f'Deleted "{label}".')
        response = HttpResponse(status=302)
        response["Location"] = str(self.success_url)
        return response


# Semester


class SemesterListView(LoginRequiredMixin, ListView):
    model = Semester
    template_name = "schedule/semester_list.html"
    context_object_name = "semesters"


class SemesterCreateView(LoginRequiredMixin, ToastFormMixin, CreateView):
    model = Semester
    form_class = SemesterForm
    template_name = "schedule/semester_form.html"
    success_url = reverse_lazy("schedule:semester_list")
    success_message = "Semester added."


class SemesterUpdateView(LoginRequiredMixin, ToastFormMixin, UpdateView):
    model = Semester
    form_class = SemesterForm
    template_name = "schedule/semester_form.html"
    success_url = reverse_lazy("schedule:semester_list")
    success_message = "Semester updated."


class SemesterDeleteView(HtmxDeleteView):
    model = Semester
    success_url = reverse_lazy("schedule:semester_list")


# Course


class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = "schedule/course_list.html"
    context_object_name = "courses"


class CourseCreateView(LoginRequiredMixin, ToastFormMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = "schedule/course_form.html"
    success_url = reverse_lazy("schedule:course_list")
    success_message = "Course added."


class CourseUpdateView(LoginRequiredMixin, ToastFormMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = "schedule/course_form.html"
    success_url = reverse_lazy("schedule:course_list")
    success_message = "Course updated."


class CourseDeleteView(HtmxDeleteView):
    model = Course
    success_url = reverse_lazy("schedule:course_list")


# TeachingAssignment


class TeachingAssignmentListView(LoginRequiredMixin, ListView):
    model = TeachingAssignment
    template_name = "schedule/assignment_list.html"
    context_object_name = "assignments"


class TeachingAssignmentCreateView(LoginRequiredMixin, ToastFormMixin, CreateView):
    model = TeachingAssignment
    form_class = TeachingAssignmentForm
    template_name = "schedule/assignment_form.html"
    success_url = reverse_lazy("schedule:assignment_list")
    success_message = "Teaching assignment added."


class TeachingAssignmentUpdateView(LoginRequiredMixin, ToastFormMixin, UpdateView):
    model = TeachingAssignment
    form_class = TeachingAssignmentForm
    template_name = "schedule/assignment_form.html"
    success_url = reverse_lazy("schedule:assignment_list")
    success_message = "Teaching assignment updated."


class TeachingAssignmentDeleteView(HtmxDeleteView):
    model = TeachingAssignment
    success_url = reverse_lazy("schedule:assignment_list")


# Event


class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = "schedule/event_list.html"
    context_object_name = "events"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["visibility_choices"] = Event.Visibility.choices
        return context


class EventCreateView(LoginRequiredMixin, ToastFormMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = "schedule/event_form.html"
    success_url = reverse_lazy("schedule:event_list")
    success_message = "Event added."


class EventUpdateView(LoginRequiredMixin, ToastFormMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = "schedule/event_form.html"
    success_url = reverse_lazy("schedule:event_list")
    success_message = "Event updated."


class EventDeleteView(HtmxDeleteView):
    model = Event
    success_url = reverse_lazy("schedule:event_list")


@login_required
def event_set_visibility(request: HttpRequest, pk: int) -> HttpResponse:
    """HTMX endpoint for the visibility <select> on the event list page."""
    event = get_object_or_404(Event, pk=pk)
    visibility = request.POST.get("visibility")
    if visibility in Event.Visibility.values:
        event.visibility = visibility
        event.save(update_fields=["visibility"])
    response = HttpResponse(status=204)
    for key, value in toast_header("Visibility updated.").items():
        response[key] = value
    return response


# Calendar views


@login_required
def calendar_week(request: HttpRequest) -> HttpResponse:
    """Weekly calendar (Mon-Sat) merging the active semester's teaching with events."""
    week_offset = int(request.GET.get("week", 0))
    today = datetime.date.today()
    this_monday = today - datetime.timedelta(days=today.weekday())
    monday = this_monday + datetime.timedelta(weeks=week_offset)
    saturday = monday + datetime.timedelta(days=5)

    semester = Semester.objects.filter(is_active=True).first()
    assignments = (
        TeachingAssignment.objects.filter(semester=semester).select_related("course")
        if semester
        else TeachingAssignment.objects.none()
    )
    events = Event.objects.filter(start_datetime__date__range=[monday, saturday])

    days = []
    for i in range(6):
        day_date = monday + datetime.timedelta(days=i)
        items = []
        for assignment in assignments.filter(day_of_week=i):
            items.append(
                {
                    "start": assignment.start_time,
                    "end": assignment.end_time,
                    "label": f"{assignment.course.code} {assignment.class_label}",
                    "sublabel": assignment.room,
                    "kind": "teaching",
                }
            )
        for event in events.filter(start_datetime__date=day_date):
            items.append(
                {
                    "start": event.start_datetime.time(),
                    "end": event.end_datetime.time(),
                    "label": event.title,
                    "sublabel": event.get_category_display(),
                    "kind": "event",
                }
            )
        items.sort(key=lambda item: item["start"])
        days.append({"date": day_date, "label": WEEKDAY_LABELS[i], "items": items})

    context = {
        "days": days,
        "semester": semester,
        "week_offset": week_offset,
        "calendar_hours": range(CALENDAR_START_HOUR, CALENDAR_END_HOUR),
    }
    return render(request, "schedule/calendar_week.html", context)


@login_required
def calendar_month(request: HttpRequest) -> HttpResponse:
    """Month view of events."""
    month_offset = int(request.GET.get("month", 0))
    today = datetime.date.today()
    year = today.year + (today.month - 1 + month_offset) // 12
    month = (today.month - 1 + month_offset) % 12 + 1

    cal = calendar_module.Calendar(firstweekday=0)
    weeks = cal.monthdayscalendar(year, month)

    events = Event.objects.filter(start_datetime__year=year, start_datetime__month=month)
    events_by_day = {}
    for event in events:
        events_by_day.setdefault(event.start_datetime.day, []).append(event)

    weeks_with_events = [
        [
            {"day": day, "events": events_by_day.get(day, [])} if day != 0 else None
            for day in week
        ]
        for week in weeks
    ]

    context = {
        "weeks": weeks_with_events,
        "month_name": datetime.date(year, month, 1).strftime("%B %Y"),
        "month_offset": month_offset,
    }
    return render(request, "schedule/calendar_month.html", context)


@login_required
def export_ics(request: HttpRequest) -> HttpResponse:
    """Export the active semester's teaching plus future events as an .ics feed."""
    cal = build_ics_calendar()
    response = HttpResponse(cal.to_ical(), content_type="text/calendar")
    response["Content-Disposition"] = 'attachment; filename="lecturerhub.ics"'
    return response
