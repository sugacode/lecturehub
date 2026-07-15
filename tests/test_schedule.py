import datetime

import pytest
from django.urls import reverse
from icalendar import Calendar

from apps.schedule.ics_export import build_ics_calendar
from apps.schedule.models import Course, Event, Semester, TeachingAssignment


@pytest.fixture
def semester(db):
    return Semester.objects.create(
        name="Ganjil 2026/2027",
        start_date=datetime.date(2026, 8, 1),
        end_date=datetime.date(2026, 12, 20),
        is_active=True,
    )


@pytest.fixture
def course(db):
    return Course.objects.create(
        code="IF301", name="Web Programming", credits=3, program="IS", level=Course.Level.S1
    )


@pytest.mark.django_db
def test_semester_str(semester):
    assert str(semester) == "Ganjil 2026/2027"


@pytest.mark.django_db
def test_course_str(course):
    assert str(course) == "IF301 - Web Programming"


@pytest.mark.django_db
def test_teaching_assignment_str(semester, course):
    assignment = TeachingAssignment.objects.create(
        course=course,
        semester=semester,
        class_label="A",
        day_of_week=TeachingAssignment.DayOfWeek.TUESDAY,
        start_time=datetime.time(8, 0),
        end_time=datetime.time(10, 0),
        room="Lab 3",
    )
    assert str(assignment) == "IF301 A (Tuesday)"


@pytest.mark.django_db
def test_event_str():
    event = Event.objects.create(
        title="Faculty Senate Meeting",
        category=Event.Category.MEETING,
        start_datetime=datetime.datetime(2026, 7, 20, 9, 0, tzinfo=datetime.timezone.utc),
        end_datetime=datetime.datetime(2026, 7, 20, 11, 0, tzinfo=datetime.timezone.utc),
    )
    assert str(event) == "Faculty Senate Meeting"


@pytest.mark.django_db
def test_calendar_week_requires_login(client):
    response = client.get(reverse("schedule:calendar_week"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_calendar_week_merges_assignments_and_events(auth_client, semester, course):
    TeachingAssignment.objects.create(
        course=course,
        semester=semester,
        class_label="A",
        day_of_week=TeachingAssignment.DayOfWeek.TUESDAY,
        start_time=datetime.time(8, 0),
        end_time=datetime.time(10, 0),
        room="Lab 3",
    )
    response = auth_client.get(reverse("schedule:calendar_week"))
    assert response.status_code == 200
    assert b"IF301 A" in response.content


@pytest.mark.django_db
def test_calendar_month_shows_events(auth_client):
    Event.objects.create(
        title="Guest Lecture Day",
        category=Event.Category.GUEST_LECTURE,
        start_datetime=datetime.datetime.now(datetime.timezone.utc),
        end_datetime=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),
    )
    response = auth_client.get(reverse("schedule:calendar_month"))
    assert response.status_code == 200
    assert b"Guest Lecture Day" in response.content


@pytest.mark.django_db
def test_semester_crud_roundtrip(auth_client):
    create_response = auth_client.post(
        reverse("schedule:semester_create"),
        {"name": "Genap 2026/2027", "start_date": "2027-01-15", "end_date": "2027-06-01"},
    )
    assert create_response.status_code == 302
    sem = Semester.objects.get(name="Genap 2026/2027")

    delete_response = auth_client.post(
        reverse("schedule:semester_delete", args=[sem.pk]), HTTP_HX_REQUEST="true"
    )
    assert delete_response.status_code == 200
    assert not Semester.objects.filter(pk=sem.pk).exists()


@pytest.mark.django_db
def test_course_crud_roundtrip(auth_client):
    create_response = auth_client.post(
        reverse("schedule:course_create"),
        {"code": "IF302", "name": "Databases", "credits": 3, "program": "IS", "level": "s1"},
    )
    assert create_response.status_code == 302
    assert Course.objects.filter(code="IF302").exists()


@pytest.mark.django_db
def test_teaching_assignment_crud_roundtrip(auth_client, semester, course):
    create_response = auth_client.post(
        reverse("schedule:assignment_create"),
        {
            "course": course.pk,
            "semester": semester.pk,
            "class_label": "B",
            "day_of_week": 2,
            "start_time": "13:00",
            "end_time": "15:00",
            "room": "Lab 1",
            "student_count": 30,
        },
    )
    assert create_response.status_code == 302
    assignment = TeachingAssignment.objects.get(class_label="B")

    delete_response = auth_client.post(
        reverse("schedule:assignment_delete", args=[assignment.pk]), HTTP_HX_REQUEST="true"
    )
    assert delete_response.status_code == 200
    assert not TeachingAssignment.objects.filter(pk=assignment.pk).exists()


@pytest.mark.django_db
def test_event_crud_roundtrip(auth_client):
    create_response = auth_client.post(
        reverse("schedule:event_create"),
        {
            "title": "Thesis Defense",
            "category": "exam_committee",
            "start_datetime": "2026-09-01T09:00",
            "end_datetime": "2026-09-01T11:00",
            "recurrence": "none",
            "visibility": "private",
        },
    )
    assert create_response.status_code == 302
    event = Event.objects.get(title="Thesis Defense")

    delete_response = auth_client.post(
        reverse("schedule:event_delete", args=[event.pk]), HTTP_HX_REQUEST="true"
    )
    assert delete_response.status_code == 200
    assert not Event.objects.filter(pk=event.pk).exists()


@pytest.mark.django_db
def test_build_ics_calendar_includes_assignment_and_event(semester, course):
    TeachingAssignment.objects.create(
        course=course,
        semester=semester,
        class_label="A",
        day_of_week=TeachingAssignment.DayOfWeek.TUESDAY,
        start_time=datetime.time(8, 0),
        end_time=datetime.time(10, 0),
        room="Lab 3",
    )
    Event.objects.create(
        title="Future Meeting",
        category=Event.Category.MEETING,
        start_datetime=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1),
        end_datetime=datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(days=1, hours=1),
    )
    ics_bytes = build_ics_calendar().to_ical()
    parsed = Calendar.from_ical(ics_bytes)
    summaries = [c.get("summary") for c in parsed.walk("VEVENT")]
    assert "IF301 A" in summaries
    assert "Future Meeting" in summaries


@pytest.mark.django_db
def test_export_ics_view_returns_calendar_content_type(auth_client):
    response = auth_client.get(reverse("schedule:export_ics"))
    assert response.status_code == 200
    assert response["Content-Type"] == "text/calendar"
    assert response.content.startswith(b"BEGIN:VCALENDAR")
