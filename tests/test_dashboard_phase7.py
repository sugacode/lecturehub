import datetime

import pytest
from django.urls import reverse

from apps.documents.models import Document
from apps.publications.models import Publication
from apps.research.models import Deliverable, Grant
from apps.schedule.models import Course, Event, Semester, TeachingAssignment
from apps.supervision.models import Milestone, Student


def make_pdf(name="doc.pdf"):
    from django.core.files.uploadedfile import SimpleUploadedFile

    return SimpleUploadedFile(name, b"%PDF-1.4 fake content", content_type="application/pdf")


@pytest.mark.django_db
def test_dashboard_home_shows_public_landing_for_anonymous(client):
    """The front page is a public resume (CV highlights + this week's schedule)
    for anonymous visitors, not a bounce to /login/ — see landing.html."""
    response = client.get(reverse("dashboard:home"))
    assert response.status_code == 200
    assert b"login" not in response.content.lower()


@pytest.mark.django_db
def test_dashboard_home_shows_publication_stats(auth_client):
    Publication.objects.create(
        pub_type=Publication.PubType.JOURNAL_ARTICLE,
        title="Test Paper",
        authors="X",
        venue="V",
        year=2024,
    )
    response = auth_client.get(reverse("dashboard:home"))
    assert response.status_code == 200
    assert b"Publications" in response.content


@pytest.mark.django_db
def test_dashboard_home_shows_upcoming_teaching(auth_client):
    today = datetime.date.today()
    semester = Semester.objects.create(
        name="Active Sem",
        start_date=today - datetime.timedelta(days=10),
        end_date=today + datetime.timedelta(days=90),
        is_active=True,
    )
    course = Course.objects.create(
        code="IF999", name="Test Course", credits=3, program="IS", level=Course.Level.S1
    )
    TeachingAssignment.objects.create(
        course=course,
        semester=semester,
        class_label="A",
        day_of_week=today.weekday(),
        start_time=datetime.time(8, 0),
        end_time=datetime.time(10, 0),
    )
    response = auth_client.get(reverse("dashboard:home"))
    assert response.status_code == 200
    assert b"IF999" in response.content


@pytest.mark.django_db
def test_dashboard_home_shows_deliverables_and_milestones_due_soon(auth_client):
    today = datetime.date.today()
    grant = Grant.objects.create(title="G1", funder="F1", start_date=today)
    Deliverable.objects.create(
        grant=grant,
        name="Due Soon Report",
        type=Deliverable.DeliverableType.REPORT,
        due_date=today + datetime.timedelta(days=10),
    )
    student = Student.objects.create(
        name="Student A", nim="123", program="IS", level=Student.Level.S1, start_date=today
    )
    Milestone.objects.create(
        student=student, name="Due Soon Milestone", due_date=today + datetime.timedelta(days=5)
    )
    response = auth_client.get(reverse("dashboard:home"))
    assert response.status_code == 200
    assert b"Due Soon Report" in response.content
    assert b"Due Soon Milestone" in response.content


@pytest.mark.django_db
def test_dashboard_home_active_grants_and_students_counts(auth_client):
    today = datetime.date.today()
    Grant.objects.create(
        title="Active Grant", funder="F", start_date=today, status=Grant.Status.ACTIVE
    )
    Grant.objects.create(
        title="Rejected Grant", funder="F", start_date=today, status=Grant.Status.REJECTED
    )
    Student.objects.create(
        name="Active Student",
        nim="1",
        program="IS",
        level=Student.Level.S1,
        start_date=today,
        status=Student.Status.IN_PROGRESS,
    )
    Student.objects.create(
        name="Graduated Student",
        nim="2",
        program="IS",
        level=Student.Level.S1,
        start_date=today,
        status=Student.Status.GRADUATED,
    )
    response = auth_client.get(reverse("dashboard:home"))
    assert response.context["active_grants"].count() == 1
    assert response.context["active_students"].count() == 1


@pytest.mark.django_db
def test_dashboard_home_expiring_documents(auth_client):
    today = datetime.date.today()
    Document.objects.create(
        title="Expiring Soon",
        file=make_pdf(),
        expiry_date=today + datetime.timedelta(days=30),
    )
    Document.objects.create(
        title="Far Future",
        file=make_pdf("b.pdf"),
        expiry_date=today + datetime.timedelta(days=300),
    )
    response = auth_client.get(reverse("dashboard:home"))
    assert response.context["expiring_documents"].count() == 1


@pytest.mark.django_db
def test_search_requires_login(client):
    response = client.get(reverse("dashboard:search"), {"q": "test"})
    assert response.status_code == 302


@pytest.mark.django_db
def test_search_empty_query_shows_prompt(auth_client):
    response = auth_client.get(reverse("dashboard:search"))
    assert response.status_code == 200
    assert b"Type something" in response.content


@pytest.mark.django_db
def test_search_finds_publication(auth_client):
    Publication.objects.create(
        pub_type=Publication.PubType.JOURNAL_ARTICLE,
        title="Machine Learning in Education",
        authors="Jane Doe",
        venue="Journal X",
        year=2024,
    )
    response = auth_client.get(reverse("dashboard:search"), {"q": "Machine Learning"})
    assert response.status_code == 200
    assert b"Machine Learning in Education" in response.content


@pytest.mark.django_db
def test_search_finds_student(auth_client):
    Student.objects.create(
        name="Budi Santoso",
        nim="1301210099",
        program="IS",
        level=Student.Level.S1,
        start_date=datetime.date.today(),
    )
    response = auth_client.get(reverse("dashboard:search"), {"q": "Budi"})
    assert response.status_code == 200
    assert b"Budi Santoso" in response.content


@pytest.mark.django_db
def test_search_finds_document_by_tag(auth_client):
    Document.objects.create(title="Random Title", file=make_pdf(), tags="uniquetag123")
    response = auth_client.get(reverse("dashboard:search"), {"q": "uniquetag123"})
    assert response.status_code == 200
    assert b"Random Title" in response.content


@pytest.mark.django_db
def test_search_finds_event(auth_client):
    Event.objects.create(
        title="Unique Seminar Title",
        category=Event.Category.SEMINAR,
        start_datetime=datetime.datetime(2026, 6, 1, 9, 0, tzinfo=datetime.timezone.utc),
        end_datetime=datetime.datetime(2026, 6, 1, 11, 0, tzinfo=datetime.timezone.utc),
    )
    response = auth_client.get(reverse("dashboard:search"), {"q": "Unique Seminar"})
    assert response.status_code == 200
    assert b"Unique Seminar Title" in response.content


@pytest.mark.django_db
def test_search_no_matches_shows_empty_state(auth_client):
    response = auth_client.get(reverse("dashboard:search"), {"q": "zzz_no_match_zzz"})
    assert response.status_code == 200
    assert response.content.count(b"No matches.") == 4
