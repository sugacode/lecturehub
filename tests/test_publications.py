from unittest.mock import Mock, patch

import pytest
import requests
from django.urls import reverse

from apps.publications.crossref import CrossRefLookupError, fetch_doi_metadata
from apps.publications.models import IntellectualProperty, Publication
from apps.research.models import Grant

CROSSREF_PAYLOAD = {
    "message": {
        "type": "journal-article",
        "title": ["A Great Paper"],
        "author": [{"given": "Jane", "family": "Doe"}, {"given": "John", "family": "Roe"}],
        "container-title": ["Journal of Testing"],
        "published-print": {"date-parts": [[2023, 5, 1]]},
        "volume": "10",
        "issue": "2",
        "page": "100-110",
        "DOI": "10.1000/xyz123",
        "URL": "https://doi.org/10.1000/xyz123",
        "is-referenced-by-count": 42,
    }
}


@pytest.mark.django_db
def test_publication_str():
    pub = Publication.objects.create(
        pub_type=Publication.PubType.JOURNAL_ARTICLE,
        title="Test Paper",
        authors="Jane Doe",
        venue="Journal X",
        year=2024,
    )
    assert str(pub) == "Test Paper (2024)"


@pytest.mark.django_db
def test_publication_stats():
    Publication.objects.create(
        pub_type=Publication.PubType.JOURNAL_ARTICLE,
        title="A",
        authors="X",
        venue="V",
        year=2023,
        indexing=Publication.Indexing.SCOPUS_Q1,
    )
    Publication.objects.create(
        pub_type=Publication.PubType.CONFERENCE_PAPER,
        title="B",
        authors="X",
        venue="V",
        year=2023,
        indexing=Publication.Indexing.NONE,
    )
    stats = Publication.objects.stats()
    assert stats["total"] == 2
    assert stats["by_type"]["journal_article"] == 1
    assert stats["by_type"]["conference_paper"] == 1
    assert stats["by_year"][2023] == 2


@pytest.mark.django_db
def test_publication_list_requires_login(client):
    response = client.get(reverse("publications:publication_list"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_publication_crud_roundtrip(auth_client):
    create_response = auth_client.post(
        reverse("publications:publication_create"),
        {
            "pub_type": "journal_article",
            "title": "My Paper",
            "authors": "Jane Doe",
            "venue": "Journal X",
            "year": 2024,
            "indexing": "none",
            "citation_count": 0,
        },
    )
    assert create_response.status_code == 302
    pub = Publication.objects.get(title="My Paper")

    delete_response = auth_client.post(
        reverse("publications:publication_delete", args=[pub.pk]), HTTP_HX_REQUEST="true"
    )
    assert delete_response.status_code == 200
    assert not Publication.objects.filter(pk=pub.pk).exists()


@pytest.mark.django_db
def test_publication_grant_link():
    grant = Grant.objects.create(title="Big Grant", funder="RISTEK", start_date="2024-01-01")
    pub = Publication.objects.create(
        pub_type=Publication.PubType.JOURNAL_ARTICLE,
        title="Funded Paper",
        authors="Jane Doe",
        venue="Journal X",
        year=2024,
        grant=grant,
    )
    assert pub.grant == grant
    assert grant.publications.count() == 1


@pytest.mark.django_db
def test_intellectual_property_str_and_crud(auth_client):
    response = auth_client.post(
        reverse("publications:ip_create"),
        {
            "title": "My Patent",
            "ip_type": "patent",
            "registration_number": "P123",
            "registration_date": "2024-01-01",
        },
    )
    assert response.status_code == 302
    ip = IntellectualProperty.objects.get(title="My Patent")
    assert str(ip) == "My Patent"

    delete_response = auth_client.post(
        reverse("publications:ip_delete", args=[ip.pk]), HTTP_HX_REQUEST="true"
    )
    assert delete_response.status_code == 200
    assert not IntellectualProperty.objects.filter(pk=ip.pk).exists()


def test_fetch_doi_metadata_success():
    mock_response = Mock()
    mock_response.json.return_value = CROSSREF_PAYLOAD
    mock_response.raise_for_status.return_value = None
    with patch("apps.publications.crossref.requests.get", return_value=mock_response):
        data = fetch_doi_metadata("10.1000/xyz123")
    assert data["title"] == "A Great Paper"
    assert data["authors"] == "Jane Doe, John Roe"
    assert data["venue"] == "Journal of Testing"
    assert data["year"] == 2023
    assert data["pub_type"] == "journal_article"
    assert data["citation_count"] == 42


def test_fetch_doi_metadata_network_failure():
    with patch(
        "apps.publications.crossref.requests.get",
        side_effect=requests.ConnectionError("boom"),
    ):
        with pytest.raises(CrossRefLookupError):
            fetch_doi_metadata("10.1000/xyz123")


@pytest.mark.django_db
def test_import_by_doi_view_prefills_create_form(auth_client):
    mock_response = Mock()
    mock_response.json.return_value = CROSSREF_PAYLOAD
    mock_response.raise_for_status.return_value = None
    with patch("apps.publications.crossref.requests.get", return_value=mock_response):
        response = auth_client.post(
            reverse("publications:import_by_doi"), {"doi": "10.1000/xyz123"}
        )
    assert response.status_code == 302
    assert response.url == reverse("publications:publication_create")

    create_response = auth_client.get(reverse("publications:publication_create"))
    assert b"A Great Paper" in create_response.content


@pytest.mark.django_db
def test_import_by_doi_view_handles_network_failure_gracefully(auth_client):
    with patch(
        "apps.publications.crossref.requests.get",
        side_effect=requests.ConnectionError("boom"),
    ):
        response = auth_client.post(
            reverse("publications:import_by_doi"), {"doi": "10.1000/xyz123"}
        )
    assert response.status_code == 200
    assert b"Could not reach CrossRef" in response.content
