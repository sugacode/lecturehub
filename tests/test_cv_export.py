import datetime

import pytest
from django.urls import reverse

from apps.accounts.models import Profile
from apps.cv.models import Achievement, Education, Position, Skill
from apps.cv.pdf_academic import build_academic_cv_pdf
from apps.cv.pdf_data import get_cv_context
from apps.cv.pdf_europass import build_europass_cv_pdf
from apps.publications.models import Publication
from apps.research.models import Grant
from apps.service.models import CommunityService, OrganizationalRole


@pytest.mark.django_db
def test_cv_export_is_public_in_open_mode(client):
    """cv:export is intentionally public (Phase 9) so /p/cv/'s Download PDF button works
    without login; it's filtered to is_public=True records for anonymous requests."""
    response = client.get(reverse("cv:export"))
    assert response.status_code == 200
    assert response["Content-Type"] == "application/pdf"


@pytest.mark.django_db
def test_cv_export_academic_returns_pdf(auth_client):
    response = auth_client.get(reverse("cv:export"), {"style": "academic"})
    assert response.status_code == 200
    assert response["Content-Type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")


@pytest.mark.django_db
def test_cv_export_europass_returns_pdf(auth_client):
    response = auth_client.get(reverse("cv:export"), {"style": "europass"})
    assert response.status_code == 200
    assert response["Content-Type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")


@pytest.mark.django_db
def test_cv_export_defaults_to_academic_style(auth_client):
    response = auth_client.get(reverse("cv:export"))
    assert response.status_code == 200
    assert response["Content-Type"] == "application/pdf"


@pytest.mark.django_db
def test_cv_export_with_full_dataset_does_not_crash(auth_client, user):
    Profile.objects.create(
        user=user, full_name="Jane Doe", bio="Researcher bio.", current_position="Lecturer"
    )
    Education.objects.create(
        degree_level="s3",
        institution="Test University",
        program="Computer Science",
        country="Indonesia",
        start_year=2018,
        end_year=2022,
        thesis_title="A Thesis",
        gpa=3.9,
    )
    Position.objects.create(
        title="Lecturer",
        organization="Test University",
        category="functional",
        start_date=datetime.date(2020, 1, 1),
        description="Teaching duties.",
    )
    Achievement.objects.create(
        title="Best Paper", issuer="IEEE", level="international", date=datetime.date(2023, 1, 1)
    )
    Skill.objects.create(name="Python", category="technical", proficiency=5)
    Publication.objects.create(
        pub_type="journal_article",
        title="A Paper",
        authors="Jane Doe",
        venue="Journal X",
        year=2024,
        doi="10.1/xyz",
    )
    grant = Grant.objects.create(
        title="A Grant", funder="Funder", start_date=datetime.date(2023, 1, 1)
    )
    CommunityService.objects.create(
        title="Workshop", date=datetime.date(2023, 6, 1), partner="Partner"
    )
    OrganizationalRole.objects.create(
        organization="ICMI", role="Member", start_date=datetime.date(2021, 1, 1)
    )

    response = auth_client.get(reverse("cv:export"), {"style": "academic"})
    assert response.status_code == 200
    assert response.content.startswith(b"%PDF")

    context = get_cv_context()
    assert context["profile"].full_name == "Jane Doe"
    assert len(context["educations"]) == 1
    assert context["publications_by_type"][0][0] == "Journal Article"
    assert grant in context["grants"]

    europass_response = auth_client.get(reverse("cv:export"), {"style": "europass"})
    assert europass_response.status_code == 200


@pytest.mark.django_db
def test_get_cv_context_public_only_filters_private_records():
    Education.objects.create(
        degree_level="s1",
        institution="Public U",
        program="CS",
        country="ID",
        start_year=2010,
        end_year=2014,
        is_public=True,
    )
    Education.objects.create(
        degree_level="s2",
        institution="Private U",
        program="CS",
        country="ID",
        start_year=2015,
        end_year=2017,
        is_public=False,
    )
    public_context = get_cv_context(public_only=True)
    assert len(public_context["educations"]) == 1
    assert public_context["educations"][0].institution == "Public U"

    full_context = get_cv_context(public_only=False)
    assert len(full_context["educations"]) == 2


def test_build_academic_cv_pdf_handles_no_profile():
    context = {
        "profile": None,
        "educations": [],
        "positions": [],
        "achievements": [],
        "skills": [],
        "trainings": [],
        "publications_by_type": [],
        "publication_stats": {"total": 0, "by_indexing": {}},
        "intellectual_properties": [],
        "grants": [],
        "community_services": [],
        "organizational_roles": [],
        "student_count": 0,
        "active_student_count": 0,
    }
    pdf_bytes = build_academic_cv_pdf(context)
    assert pdf_bytes.startswith(b"%PDF")


def test_build_europass_cv_pdf_handles_no_profile():
    context = {
        "profile": None,
        "educations": [],
        "positions": [],
        "achievements": [],
        "skills": [],
        "trainings": [],
        "publications_by_type": [],
        "publication_stats": {"total": 0, "by_indexing": {}},
        "intellectual_properties": [],
        "grants": [],
        "community_services": [],
        "organizational_roles": [],
        "student_count": 0,
        "active_student_count": 0,
    }
    pdf_bytes = build_europass_cv_pdf(context)
    assert pdf_bytes.startswith(b"%PDF")


def _uri_annotations(pdf_bytes: bytes) -> list[str]:
    import re

    return [m.decode() for m in re.findall(rb"/URI\s*\(([^)]+)\)", pdf_bytes)]


@pytest.mark.django_db
@pytest.mark.parametrize("style", ["academic", "europass"])
def test_cv_export_hyperlinks_external_profile_ids_and_dois(auth_client, user, style):
    Profile.objects.create(
        user=user,
        full_name="Jane Doe",
        email="jane@example.com",
        phone="+62 811 000 111",
        orcid="0000-0002-6456-576X",
        google_scholar_id="DRt8xy4AAAAJ",
        linkedin_url="https://www.linkedin.com/in/janedoe",
    )
    Publication.objects.create(
        pub_type="journal_article",
        title="Linked Paper",
        authors="Jane Doe",
        venue="Journal X",
        year=2024,
        doi="10.1234/abcd.5678",
        is_public=True,
    )
    response = auth_client.get(reverse("cv:export"), {"style": style})
    assert response.status_code == 200
    uris = _uri_annotations(response.content)
    assert "mailto:jane@example.com" in uris
    assert "https://wa.me/62811000111" in uris
    assert "https://orcid.org/0000-0002-6456-576X" in uris
    assert "https://scholar.google.com/citations?user=DRt8xy4AAAAJ" in uris
    assert "https://www.linkedin.com/in/janedoe" in uris
    assert "https://doi.org/10.1234/abcd.5678" in uris


def test_flatten_publications_by_year_sorts_newest_first_across_types():
    """Europass has no per-type headers, so publications must be one chronological
    list; pdf_data.py groups by type first, so mixing types with different years
    used to leave an older journal article ahead of a newer conference paper."""
    from apps.cv.pdf_europass import _flatten_publications_by_year

    older = Publication(pub_type="journal_article", title="Older Journal Paper", year=2020)
    newer = Publication(pub_type="conference_paper", title="Newer Conference Paper", year=2024)
    publications_by_type = [
        ("Journal Article", [older]),
        ("Conference Paper", [newer]),
    ]
    result = _flatten_publications_by_year(publications_by_type)
    assert result == [newer, older]
