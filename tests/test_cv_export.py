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
def test_cv_export_requires_login(client):
    response = client.get(reverse("cv:export"))
    assert response.status_code == 302


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
