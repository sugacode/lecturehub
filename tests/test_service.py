import datetime

import pytest
from django.urls import reverse

from apps.service.models import CommunityService, OrganizationalRole


@pytest.mark.django_db
def test_community_service_str():
    service = CommunityService.objects.create(
        title="Digital Literacy Workshop",
        partner="SMA Muhammadiyah 1",
        date=datetime.date(2026, 4, 1),
    )
    assert str(service) == "Digital Literacy Workshop"


@pytest.mark.django_db
def test_organizational_role_str_and_is_current():
    current = OrganizationalRole.objects.create(
        organization="APSI PTMA",
        role="Regional Coordinator",
        start_date=datetime.date(2025, 1, 1),
    )
    past = OrganizationalRole.objects.create(
        organization="ICMI",
        role="Member",
        start_date=datetime.date(2020, 1, 1),
        end_date=datetime.date(2023, 1, 1),
    )
    assert str(current) == "Regional Coordinator, APSI PTMA"
    assert current.is_current is True
    assert past.is_current is False


@pytest.mark.django_db
def test_community_service_list_requires_login(client):
    response = client.get(reverse("service:community_service_list"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_community_service_crud_roundtrip(auth_client):
    create_response = auth_client.post(
        reverse("service:community_service_create"),
        {"title": "Coding Bootcamp", "date": "2026-05-01"},
    )
    assert create_response.status_code == 302
    service = CommunityService.objects.get(title="Coding Bootcamp")

    delete_response = auth_client.post(
        reverse("service:community_service_delete", args=[service.pk]), HTTP_HX_REQUEST="true"
    )
    assert delete_response.status_code == 200
    assert not CommunityService.objects.filter(pk=service.pk).exists()


@pytest.mark.django_db
def test_organizational_role_crud_roundtrip(auth_client):
    create_response = auth_client.post(
        reverse("service:organizational_role_create"),
        {"organization": "ICMI", "role": "Board Member", "start_date": "2026-01-01"},
    )
    assert create_response.status_code == 302
    role = OrganizationalRole.objects.get(role="Board Member")

    delete_response = auth_client.post(
        reverse("service:organizational_role_delete", args=[role.pk]), HTTP_HX_REQUEST="true"
    )
    assert delete_response.status_code == 200
    assert not OrganizationalRole.objects.filter(pk=role.pk).exists()


@pytest.mark.django_db
def test_organizational_role_list_renders(auth_client):
    OrganizationalRole.objects.create(
        organization="APSI PTMA", role="Coordinator", start_date=datetime.date(2025, 1, 1)
    )
    response = auth_client.get(reverse("service:organizational_role_list"))
    assert response.status_code == 200
    assert b"APSI PTMA" in response.content
