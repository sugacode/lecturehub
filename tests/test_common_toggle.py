
import pytest
from django.urls import reverse

from apps.cv.models import Education


@pytest.fixture
def education(db):
    return Education.objects.create(
        degree_level="s1",
        institution="Test U",
        program="CS",
        country="ID",
        start_year=2010,
        end_year=2014,
        is_public=False,
    )


@pytest.mark.django_db
def test_toggle_public_requires_login(client, education):
    url = reverse("common:toggle_public", args=["cv", "education", education.pk])
    response = client.post(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_toggle_public_flips_flag(auth_client, education):
    url = reverse("common:toggle_public", args=["cv", "education", education.pk])
    response = auth_client.post(url, HTTP_HX_REQUEST="true")
    assert response.status_code == 200
    education.refresh_from_db()
    assert education.is_public is True
    assert "HX-Trigger" in response.headers

    response2 = auth_client.post(url, HTTP_HX_REQUEST="true")
    education.refresh_from_db()
    assert education.is_public is False
    assert response2.status_code == 200


@pytest.mark.django_db
def test_toggle_public_rejects_non_allowlisted_model(auth_client):
    from django.core.files.uploadedfile import SimpleUploadedFile

    from apps.documents.models import Document

    doc = Document.objects.create(
        title="Doc", file=SimpleUploadedFile("a.pdf", b"%PDF-1.4", content_type="application/pdf")
    )
    url = reverse("common:toggle_public", args=["documents", "document", doc.pk])
    response = auth_client.post(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_bulk_make_public_requires_login(client, education):
    url = reverse("common:bulk_make_public", args=["cv", "education"])
    response = client.post(url, {"selected": [education.pk]})
    assert response.status_code == 302
    education.refresh_from_db()
    assert education.is_public is False


@pytest.mark.django_db
def test_bulk_make_public_updates_selected(auth_client):
    e1 = Education.objects.create(
        degree_level="s1",
        institution="A",
        program="CS",
        country="ID",
        start_year=2010,
        end_year=2014,
    )
    e2 = Education.objects.create(
        degree_level="s2",
        institution="B",
        program="CS",
        country="ID",
        start_year=2015,
        end_year=2017,
    )
    url = reverse("common:bulk_make_public", args=["cv", "education"])
    response = auth_client.post(
        url, {"selected": [e1.pk], "next": reverse("cv:education_list")}
    )
    assert response.status_code == 302
    e1.refresh_from_db()
    e2.refresh_from_db()
    assert e1.is_public is True
    assert e2.is_public is False
