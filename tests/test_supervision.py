import datetime

import pytest
from django.urls import reverse

from apps.supervision.models import Milestone, Student, SupervisionLog


@pytest.fixture
def student(db):
    return Student.objects.create(
        name="Siti Rahma",
        nim="1301210001",
        program="Information Systems",
        level=Student.Level.S1,
        status=Student.Status.PROPOSAL,
        start_date=datetime.date(2026, 2, 1),
    )


@pytest.mark.django_db
def test_student_str(student):
    assert str(student) == "Siti Rahma (1301210001)"


@pytest.mark.django_db
def test_student_is_active(student):
    assert student.is_active is True
    student.status = Student.Status.GRADUATED
    student.save()
    assert student.is_active is False


@pytest.mark.django_db
def test_overdue_milestone_count(student):
    Milestone.objects.create(
        student=student, name="Proposal Seminar", due_date=datetime.date(2020, 1, 1)
    )
    Milestone.objects.create(
        student=student,
        name="Completed One",
        due_date=datetime.date(2020, 1, 1),
        completed_date=datetime.date(2020, 1, 5),
    )
    assert student.overdue_milestone_count == 1


@pytest.mark.django_db
def test_milestone_is_overdue_property(student):
    overdue = Milestone.objects.create(
        student=student, name="Late", due_date=datetime.date(2020, 1, 1)
    )
    upcoming = Milestone.objects.create(
        student=student, name="Future", due_date=datetime.date(2099, 1, 1)
    )
    assert overdue.is_overdue is True
    assert upcoming.is_overdue is False


@pytest.mark.django_db
def test_supervision_log_str(student):
    log = SupervisionLog.objects.create(
        student=student,
        date=datetime.date(2026, 3, 1),
        mode=SupervisionLog.Mode.ONLINE,
        summary="Discussed chapter 1",
    )
    assert str(log) == "Siti Rahma - 2026-03-01"


@pytest.mark.django_db
def test_student_list_requires_login(client):
    response = client.get(reverse("supervision:student_list"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_student_crud_roundtrip(auth_client):
    create_response = auth_client.post(
        reverse("supervision:student_create"),
        {
            "name": "Budi Santoso",
            "nim": "1301210002",
            "program": "Information Systems",
            "level": "s2",
            "status": "in_progress",
            "start_date": "2026-01-01",
        },
    )
    assert create_response.status_code == 302
    new_student = Student.objects.get(nim="1301210002")

    delete_response = auth_client.post(
        reverse("supervision:student_delete", args=[new_student.pk]), HTTP_HX_REQUEST="true"
    )
    assert delete_response.status_code == 200
    assert not Student.objects.filter(pk=new_student.pk).exists()


@pytest.mark.django_db
def test_student_timeline_view(auth_client, student):
    Milestone.objects.create(
        student=student, name="Proposal Seminar", due_date=datetime.date(2026, 3, 1)
    )
    SupervisionLog.objects.create(
        student=student,
        date=datetime.date(2026, 3, 2),
        mode=SupervisionLog.Mode.IN_PERSON,
        summary="Kickoff meeting",
    )
    response = auth_client.get(reverse("supervision:student_timeline", args=[student.pk]))
    assert response.status_code == 200
    assert b"Proposal Seminar" in response.content
    assert b"Kickoff meeting" in response.content


@pytest.mark.django_db
def test_milestone_create_and_delete_via_timeline(auth_client, student):
    create_response = auth_client.post(
        reverse("supervision:milestone_create", args=[student.pk]),
        {"name": "Draft Chapter 2", "due_date": "2026-05-01"},
    )
    assert create_response.status_code == 302
    milestone = Milestone.objects.get(name="Draft Chapter 2")

    delete_response = auth_client.post(
        reverse("supervision:milestone_delete", args=[milestone.pk]), HTTP_HX_REQUEST="true"
    )
    assert delete_response.status_code == 200
    assert not Milestone.objects.filter(pk=milestone.pk).exists()


@pytest.mark.django_db
def test_log_create_and_delete_via_timeline(auth_client, student):
    create_response = auth_client.post(
        reverse("supervision:log_create", args=[student.pk]),
        {"date": "2026-04-01", "mode": "online", "summary": "Reviewed methodology"},
    )
    assert create_response.status_code == 302
    log = SupervisionLog.objects.get(summary="Reviewed methodology")

    delete_response = auth_client.post(
        reverse("supervision:log_delete", args=[log.pk]), HTTP_HX_REQUEST="true"
    )
    assert delete_response.status_code == 200
    assert not SupervisionLog.objects.filter(pk=log.pk).exists()
