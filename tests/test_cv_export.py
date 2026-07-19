import datetime

import pytest
from django.urls import reverse

from apps.accounts.models import Profile
from apps.cv.models import Achievement, Education, Position, Skill
from apps.cv.pdf_academic import build_academic_cv_pdf
from apps.cv.pdf_data import get_cv_context
from apps.cv.pdf_elegant import build_elegant_cv_pdf
from apps.cv.pdf_europass import build_europass_cv_pdf
from apps.publications.models import IntellectualProperty, Publication
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
def test_cv_export_elegant_returns_pdf(auth_client):
    response = auth_client.get(reverse("cv:export"), {"style": "elegant"})
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


def test_build_elegant_cv_pdf_handles_no_profile():
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
    pdf_bytes = build_elegant_cv_pdf(context)
    assert pdf_bytes.startswith(b"%PDF")


def _uri_annotations(pdf_bytes: bytes) -> list[str]:
    import re

    return [m.decode() for m in re.findall(rb"/URI\s*\(([^)]+)\)", pdf_bytes)]


@pytest.mark.django_db
@pytest.mark.parametrize("style", ["academic", "europass", "elegant"])
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


@pytest.mark.django_db
@pytest.mark.parametrize("style", ["academic", "europass", "elegant"])
def test_cv_export_includes_intellectual_property_section(auth_client, style, tmp_path):
    import shutil
    import subprocess

    if shutil.which("pdftotext") is None:
        pytest.skip("pdftotext (poppler) not installed")

    IntellectualProperty.objects.create(
        title="Campus Navigation App",
        ip_type="copyright",
        registration_number="EC00202516819",
        registration_date=datetime.date(2025, 1, 1),
        is_public=True,
    )
    response = auth_client.get(reverse("cv:export"), {"style": style})
    assert response.status_code == 200
    pdf_path = tmp_path / "cv.pdf"
    pdf_path.write_bytes(response.content)
    text = subprocess.run(
        ["pdftotext", str(pdf_path), "-"], capture_output=True, text=True, check=True
    ).stdout
    assert "Campus Navigation App" in text
    assert "EC00202516819" in text


@pytest.mark.django_db
def test_europass_pdf_groups_publications_by_type_with_restarting_numbers(auth_client, tmp_path):
    """The Europass redesign lists each publication type with its own numbered
    list restarting at 1 (matching the source design), unlike the Elegant
    style's single continuously-numbered list."""
    import shutil
    import subprocess

    if shutil.which("pdftotext") is None:
        pytest.skip("pdftotext (poppler) not installed")

    Publication.objects.create(
        pub_type="journal_article", title="A Journal Paper", authors="X", venue="V", year=2024
    )
    Publication.objects.create(
        pub_type="conference_paper", title="A Conference Paper", authors="X", venue="V", year=2023
    )
    response = auth_client.get(reverse("cv:export"), {"style": "europass"})
    pdf_path = tmp_path / "cv.pdf"
    pdf_path.write_bytes(response.content)
    text = subprocess.run(
        ["pdftotext", str(pdf_path), "-"], capture_output=True, text=True, check=True
    ).stdout
    assert "1. X (2024). A Journal Paper" in text
    assert "1. X (2023). A Conference Paper" in text


@pytest.mark.django_db
def test_europass_pdf_combines_grants_and_achievements(auth_client, tmp_path):
    import shutil
    import subprocess

    if shutil.which("pdftotext") is None:
        pytest.skip("pdftotext (poppler) not installed")

    Grant.objects.create(
        title="A Research Grant", funder="Funder Org", start_date=datetime.date(2023, 1, 1)
    )
    Achievement.objects.create(
        title="A Nice Award", issuer="Some Body", level="national", date=datetime.date(2022, 1, 1)
    )
    response = auth_client.get(reverse("cv:export"), {"style": "europass"})
    pdf_path = tmp_path / "cv.pdf"
    pdf_path.write_bytes(response.content)
    text = subprocess.run(
        ["pdftotext", str(pdf_path), "-"], capture_output=True, text=True, check=True
    ).stdout
    assert "GRANTS, SCHOLARSHIPS & AWARDS" in text
    assert "A Research Grant" in text
    assert "A Nice Award" in text


@pytest.mark.django_db
def test_europass_pdf_splits_positions_by_research_in_title(auth_client, user, tmp_path):
    import shutil
    import subprocess

    if shutil.which("pdftotext") is None:
        pytest.skip("pdftotext (poppler) not installed")

    Profile.objects.create(user=user, full_name="Jane Doe")
    Position.objects.create(
        title="Principal Researcher",
        organization="Some Org",
        category="professional",
        start_date=datetime.date(2020, 1, 1),
    )
    Position.objects.create(
        title="Lecturer",
        organization="Some Org",
        category="functional",
        start_date=datetime.date(2015, 1, 1),
    )
    response = auth_client.get(reverse("cv:export"), {"style": "europass"})
    pdf_path = tmp_path / "cv.pdf"
    pdf_path.write_bytes(response.content)
    text = subprocess.run(
        ["pdftotext", str(pdf_path), "-"], capture_output=True, text=True, check=True
    ).stdout
    assert text.index("RESEARCH EXPERIENCE") < text.index("Principal Researcher")
    assert text.index("PROFESSIONAL EXPERIENCE") < text.index("Lecturer")


@pytest.mark.django_db
def test_europass_pdf_shows_language_proficiency_labels(auth_client, tmp_path):
    import shutil
    import subprocess

    if shutil.which("pdftotext") is None:
        pytest.skip("pdftotext (poppler) not installed")

    Skill.objects.create(name="Bahasa Indonesia", category="language", proficiency=5)
    response = auth_client.get(reverse("cv:export"), {"style": "europass"})
    pdf_path = tmp_path / "cv.pdf"
    pdf_path.write_bytes(response.content)
    text = subprocess.run(
        ["pdftotext", str(pdf_path), "-"], capture_output=True, text=True, check=True
    ).stdout
    assert "Bahasa Indonesia" in text
    assert "Expert" in text
