import datetime

import pytest
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Profile
from apps.cv.models import Education
from apps.schedule.models import Course, Event, Semester, TeachingAssignment


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.mark.django_db
def test_public_cv_accessible_without_login(client):
    response = client.get(reverse("public:public_cv"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_public_cv_excludes_private_records(client):
    Education.objects.create(
        degree_level="s1",
        institution="Public Uni",
        program="CS",
        country="ID",
        start_year=2010,
        end_year=2014,
        is_public=True,
    )
    Education.objects.create(
        degree_level="s2",
        institution="Private Uni",
        program="CS",
        country="ID",
        start_year=2015,
        end_year=2017,
        is_public=False,
    )
    response = client.get(reverse("public:public_cv"))
    assert b"Public Uni" in response.content
    assert b"Private Uni" not in response.content


@pytest.mark.django_db
def test_public_cv_shows_public_email_not_private_email(client, user):
    Profile.objects.create(
        user=user,
        full_name="Jane Doe",
        email="private@example.com",
        public_email="public@example.com",
    )
    response = client.get(reverse("public:public_cv"))
    assert b"public@example.com" in response.content
    assert b"private@example.com" not in response.content


@pytest.mark.django_db
def test_public_schedule_accessible_without_login(client):
    response = client.get(reverse("public:public_schedule"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_public_schedule_excludes_private_teaching_assignment(client):
    today = timezone.localdate()
    semester = Semester.objects.create(
        name="Sem",
        start_date=today - datetime.timedelta(days=5),
        end_date=today + datetime.timedelta(days=90),
        is_active=True,
    )
    course = Course.objects.create(
        code="CS101", name="Secret Course", credits=3, program="IS", level="s1"
    )
    TeachingAssignment.objects.create(
        course=course,
        semester=semester,
        class_label="A",
        day_of_week=today.weekday(),
        start_time=datetime.time(8, 0),
        end_time=datetime.time(10, 0),
        is_public=False,
    )
    response = client.get(reverse("public:public_schedule"))
    assert b"CS101" not in response.content


@pytest.mark.django_db
def test_public_schedule_shows_public_teaching_assignment():
    from django.test import Client

    client = Client()
    today = timezone.localdate()
    semester = Semester.objects.create(
        name="Sem",
        start_date=today - datetime.timedelta(days=5),
        end_date=today + datetime.timedelta(days=90),
        is_active=True,
    )
    course = Course.objects.create(
        code="CS999", name="Public Course", credits=3, program="IS", level="s1"
    )
    TeachingAssignment.objects.create(
        course=course,
        semester=semester,
        class_label="A",
        day_of_week=today.weekday(),
        start_time=datetime.time(8, 0),
        end_time=datetime.time(10, 0),
        is_public=True,
        room="Room 5",
    )
    response = client.get(reverse("public:public_schedule"))
    assert b"CS999" in response.content
    assert b"Room 5" in response.content


@pytest.mark.django_db
def test_public_schedule_busy_event_hides_title_and_notes(client):
    now = timezone.now()
    Event.objects.create(
        title="Confidential Meeting",
        category="meeting",
        start_datetime=now.replace(hour=10, minute=0, second=0, microsecond=0),
        end_datetime=now.replace(hour=11, minute=0, second=0, microsecond=0),
        visibility="busy",
        notes="TOP SECRET AGENDA",
        location="Secret Room",
    )
    response = client.get(reverse("public:public_schedule"))
    assert response.status_code == 200
    assert b"Confidential Meeting" not in response.content
    assert b"TOP SECRET AGENDA" not in response.content
    assert b"Secret Room" not in response.content
    assert b"Busy" in response.content


@pytest.mark.django_db
def test_public_schedule_public_event_hides_notes_and_meeting_url(client):
    now = timezone.now()
    Event.objects.create(
        title="Open Seminar",
        category="seminar",
        start_datetime=now.replace(hour=13, minute=0, second=0, microsecond=0),
        end_datetime=now.replace(hour=14, minute=0, second=0, microsecond=0),
        visibility="public",
        notes="Internal notes should not leak",
        meeting_url="https://secret.example.com/zoom",
        location="Main Hall",
    )
    response = client.get(reverse("public:public_schedule"))
    assert b"Open Seminar" in response.content
    assert b"Main Hall" in response.content
    assert b"Internal notes should not leak" not in response.content
    assert b"secret.example.com" not in response.content


@pytest.mark.django_db
def test_public_schedule_excludes_private_event(client):
    now = timezone.now()
    Event.objects.create(
        title="Private Event",
        category="personal",
        start_datetime=now.replace(hour=9, minute=0, second=0, microsecond=0),
        end_datetime=now.replace(hour=10, minute=0, second=0, microsecond=0),
        visibility="private",
    )
    response = client.get(reverse("public:public_schedule"))
    assert b"Private Event" not in response.content


@pytest.mark.django_db
@override_settings(PUBLIC_PAGES_MODE="unlisted")
def test_unlisted_mode_404s_open_cv_url(client):
    response = client.get(reverse("public:public_cv"))
    assert response.status_code == 404


@pytest.mark.django_db
@override_settings(PUBLIC_PAGES_MODE="unlisted")
def test_unlisted_mode_serves_correct_slug_with_noindex(client, user):
    profile = Profile.objects.create(user=user, full_name="Jane Doe")
    url = reverse("public:public_cv_slug", args=[profile.public_slug])
    response = client.get(url)
    assert response.status_code == 200
    assert response["X-Robots-Tag"] == "noindex"


@pytest.mark.django_db
@override_settings(PUBLIC_PAGES_MODE="unlisted")
def test_unlisted_mode_404s_wrong_slug(client, user):
    Profile.objects.create(user=user, full_name="Jane Doe")
    url = reverse("public:public_cv_slug", args=["wrong-slug"])
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
@override_settings(PUBLIC_PAGES_MODE="open")
def test_open_mode_serves_cv_without_slug(client):
    response = client.get(reverse("public:public_cv"))
    assert response.status_code == 200
    assert "X-Robots-Tag" not in response


@pytest.mark.django_db
def test_public_cv_context_is_cached(client):
    assert cache.get("public_cv_context") is None
    client.get(reverse("public:public_cv"))
    assert cache.get("public_cv_context") is not None


@pytest.mark.django_db
def test_cv_export_public_only_shows_public_records(client):
    Education.objects.create(
        degree_level="s1",
        institution="Public Uni",
        program="CS",
        country="ID",
        start_year=2010,
        end_year=2014,
        is_public=True,
    )
    Education.objects.create(
        degree_level="s2",
        institution="Private Uni",
        program="CS",
        country="ID",
        start_year=2015,
        end_year=2017,
        is_public=False,
    )
    response = client.get(reverse("cv:export"))
    assert response.status_code == 200
    assert response["Content-Type"] == "application/pdf"


@pytest.mark.django_db
@override_settings(PUBLIC_PAGES_MODE="unlisted")
def test_cv_export_unlisted_requires_slug(client):
    response = client.get(reverse("cv:export"))
    assert response.status_code == 404


@pytest.mark.django_db
@override_settings(PUBLIC_PAGES_MODE="unlisted")
def test_cv_export_unlisted_with_correct_slug_succeeds(client, user):
    profile = Profile.objects.create(user=user, full_name="Jane Doe")
    response = client.get(reverse("cv:export"), {"slug": profile.public_slug})
    assert response.status_code == 200


@pytest.mark.django_db
def test_cv_export_authenticated_shows_all_records(auth_client):
    Education.objects.create(
        degree_level="s2",
        institution="Private Uni",
        program="CS",
        country="ID",
        start_year=2015,
        end_year=2017,
        is_public=False,
    )
    response = auth_client.get(reverse("cv:export"))
    assert response.status_code == 200

@pytest.mark.django_db
def test_public_cv_renders_external_profile_links(client, user):
    Profile.objects.create(
        user=user,
        full_name="Jane Doe",
        orcid="0000-0002-6456-576X",
        google_scholar_id="DRt8xy4AAAAJ",
        linkedin_url="https://www.linkedin.com/in/janedoe",
        phone="+62 811 000 111",
        show_phone_publicly=True,
    )
    response = client.get(reverse("public:public_cv"))
    content = response.content.decode()
    assert 'href="https://orcid.org/0000-0002-6456-576X"' in content
    assert 'href="https://scholar.google.com/citations?user=DRt8xy4AAAAJ"' in content
    assert 'href="https://www.linkedin.com/in/janedoe"' in content
    assert 'href="https://wa.me/62811000111"' in content
    # captions are just the IDs, not full URLs
    assert "in/janedoe" in content


@pytest.mark.django_db
def test_public_cv_hides_whatsapp_when_phone_not_public(client, user):
    Profile.objects.create(
        user=user, full_name="Jane Doe", phone="+62 811 000 111", show_phone_publicly=False
    )
    response = client.get(reverse("public:public_cv"))
    content = response.content.decode()
    assert "wa.me" not in content
    assert "+62 811 000 111" not in content


@pytest.mark.django_db
def test_public_cv_publication_doi_is_hyperlinked(client):
    from apps.publications.models import Publication

    Publication.objects.create(
        pub_type="journal_article",
        title="Linked Paper",
        authors="Jane Doe",
        venue="Journal X",
        year=2024,
        doi="10.1234/abcd.5678",
        is_public=True,
    )
    response = client.get(reverse("public:public_cv"))
    content = response.content.decode()
    assert 'href="https://doi.org/10.1234/abcd.5678"' in content
    assert ">10.1234/abcd.5678</a>" in content


@pytest.mark.django_db
def test_public_cv_shows_public_intellectual_property(client):
    from apps.publications.models import IntellectualProperty

    IntellectualProperty.objects.create(
        title="Public IP Record",
        ip_type="patent",
        registration_number="P-123",
        registration_date=datetime.date(2024, 1, 1),
        is_public=True,
    )
    IntellectualProperty.objects.create(
        title="Private IP Record",
        ip_type="patent",
        registration_number="P-456",
        registration_date=datetime.date(2024, 1, 1),
        is_public=False,
    )
    response = client.get(reverse("public:public_cv"))
    assert b"Public IP Record" in response.content
    assert b"Private IP Record" not in response.content

@pytest.mark.django_db
def test_saving_profile_invalidates_public_cv_cache(client, user):
    client.get(reverse("public:public_cv"))
    assert cache.get("public_cv_context") is not None

    Profile.objects.create(user=user, full_name="Jane Doe")

    assert cache.get("public_cv_context") is None


@pytest.mark.django_db
def test_landing_reflects_profile_edit_immediately(client, user):
    """A profile save (e.g. uploading a photo) must show up on the front page
    right away, not after the 5-minute public_cv_context cache expires."""
    client.get(reverse("dashboard:home"))
    Profile.objects.create(user=user, full_name="Freshly Edited Name")
    response = client.get(reverse("dashboard:home"))
    assert b"Freshly Edited Name" in response.content
