import datetime

import pytest
from django.urls import reverse

from apps.research.models import Deliverable, Grant


@pytest.fixture
def grant(db):
    return Grant.objects.create(
        title="AI Learning Analytics",
        funder="Kemdikbudristek",
        role=Grant.Role.PI,
        amount=150000000,
        start_date=datetime.date(2026, 3, 1),
        status=Grant.Status.ACTIVE,
    )


@pytest.mark.django_db
def test_grant_is_active_property(grant):
    assert grant.is_active is True
    grant.status = Grant.Status.COMPLETED
    grant.save()
    assert grant.is_active is False


@pytest.mark.django_db
def test_deliverable_str(grant):
    deliverable = Deliverable.objects.create(
        grant=grant,
        name="Final Report",
        type=Deliverable.DeliverableType.REPORT,
        due_date=datetime.date(2026, 11, 30),
    )
    assert str(deliverable) == "Final Report (AI Learning Analytics)"


@pytest.mark.django_db
def test_grant_crud_roundtrip(auth_client):
    create_response = auth_client.post(
        reverse("research:grant_create"),
        {
            "title": "New Grant",
            "funder": "RISTEK",
            "role": "co_pi",
            "currency": "IDR",
            "start_date": "2026-01-01",
            "status": "proposed",
        },
    )
    assert create_response.status_code == 302
    grant = Grant.objects.get(title="New Grant")

    delete_response = auth_client.post(
        reverse("research:grant_delete", args=[grant.pk]), HTTP_HX_REQUEST="true"
    )
    assert delete_response.status_code == 200
    assert not Grant.objects.filter(pk=grant.pk).exists()


@pytest.mark.django_db
def test_grant_detail_view(auth_client, grant):
    Deliverable.objects.create(
        grant=grant,
        name="Prototype v1",
        type=Deliverable.DeliverableType.PROTOTYPE,
        due_date=datetime.date(2026, 9, 1),
    )
    response = auth_client.get(reverse("research:grant_detail", args=[grant.pk]))
    assert response.status_code == 200
    assert b"Prototype v1" in response.content


@pytest.mark.django_db
def test_deliverable_create_and_delete(auth_client, grant):
    create_response = auth_client.post(
        reverse("research:deliverable_create", args=[grant.pk]),
        {"name": "Journal Paper", "type": "publication", "due_date": "2026-10-01"},
    )
    assert create_response.status_code == 302
    deliverable = Deliverable.objects.get(name="Journal Paper")
    assert deliverable.grant == grant

    delete_response = auth_client.post(
        reverse("research:deliverable_delete", args=[deliverable.pk]), HTTP_HX_REQUEST="true"
    )
    assert delete_response.status_code == 200
    assert not Deliverable.objects.filter(pk=deliverable.pk).exists()


@pytest.mark.django_db
def test_grant_list_requires_login(client):
    response = client.get(reverse("research:grant_list"))
    assert response.status_code == 302
