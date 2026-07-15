import datetime

import pytest
from django.urls import reverse

from apps.cv.models import Achievement, Education, Position, Skill, TrainingCertification


@pytest.mark.django_db
def test_education_str():
    education = Education.objects.create(
        degree_level=Education.DegreeLevel.S3,
        institution="Universitas Indonesia",
        program="Computer Science",
        country="Indonesia",
        start_year=2018,
        end_year=2022,
    )
    assert str(education) == "S3 - Computer Science, Universitas Indonesia"


@pytest.mark.django_db
def test_education_list_requires_login(client):
    response = client.get(reverse("cv:education_list"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_education_crud_roundtrip(auth_client):
    create_response = auth_client.post(
        reverse("cv:education_create"),
        {
            "degree_level": "s2",
            "institution": "ITB",
            "program": "Informatics",
            "country": "Indonesia",
            "start_year": 2014,
            "end_year": 2016,
        },
    )
    assert create_response.status_code == 302
    education = Education.objects.get(program="Informatics")

    update_response = auth_client.post(
        reverse("cv:education_update", args=[education.pk]),
        {
            "degree_level": "s2",
            "institution": "ITB",
            "program": "Informatics Updated",
            "country": "Indonesia",
            "start_year": 2014,
            "end_year": 2016,
        },
    )
    assert update_response.status_code == 302
    education.refresh_from_db()
    assert education.program == "Informatics Updated"

    delete_response = auth_client.post(
        reverse("cv:education_delete", args=[education.pk]), HTTP_HX_REQUEST="true"
    )
    assert delete_response.status_code == 200
    assert not Education.objects.filter(pk=education.pk).exists()


@pytest.mark.django_db
def test_position_is_current_property():
    current = Position.objects.create(
        title="Head of Bureau",
        organization="University",
        category=Position.Category.STRUCTURAL,
        start_date=datetime.date(2023, 1, 1),
    )
    past = Position.objects.create(
        title="Lecturer",
        organization="University",
        category=Position.Category.FUNCTIONAL,
        start_date=datetime.date(2018, 1, 1),
        end_date=datetime.date(2022, 1, 1),
    )
    assert current.is_current is True
    assert past.is_current is False


@pytest.mark.django_db
def test_position_list_and_create(auth_client):
    response = auth_client.post(
        reverse("cv:position_create"),
        {
            "title": "Head of Bureau",
            "organization": "University",
            "category": "structural",
            "start_date": "2023-01-01",
        },
    )
    assert response.status_code == 302
    assert Position.objects.filter(title="Head of Bureau").exists()

    list_response = auth_client.get(reverse("cv:position_list"))
    assert list_response.status_code == 200
    assert b"Head of Bureau" in list_response.content


@pytest.mark.django_db
def test_achievement_create_and_delete(auth_client):
    response = auth_client.post(
        reverse("cv:achievement_create"),
        {
            "title": "Best Paper Award",
            "issuer": "IEEE",
            "level": "international",
            "date": "2024-05-01",
        },
    )
    assert response.status_code == 302
    achievement = Achievement.objects.get(title="Best Paper Award")

    delete_response = auth_client.post(
        reverse("cv:achievement_delete", args=[achievement.pk]), HTTP_HX_REQUEST="true"
    )
    assert delete_response.status_code == 200
    assert not Achievement.objects.filter(pk=achievement.pk).exists()


@pytest.mark.django_db
def test_skill_str_and_create(auth_client):
    skill = Skill.objects.create(name="Django", category=Skill.Category.TECHNICAL, proficiency=5)
    assert str(skill) == "Django (5/5)"

    response = auth_client.post(
        reverse("cv:skill_create"),
        {"name": "Python", "category": "technical", "proficiency": 5},
    )
    assert response.status_code == 302
    assert Skill.objects.filter(name="Python").exists()


@pytest.mark.django_db
def test_training_certification_create_and_list(auth_client):
    response = auth_client.post(
        reverse("cv:training_create"),
        {"name": "AWS Certified", "provider": "Amazon", "date": "2024-01-01"},
    )
    assert response.status_code == 302
    assert TrainingCertification.objects.filter(name="AWS Certified").exists()

    list_response = auth_client.get(reverse("cv:training_list"))
    assert list_response.status_code == 200
    assert b"AWS Certified" in list_response.content
