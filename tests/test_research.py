import pytest

from apps.research.models import Grant


@pytest.mark.django_db
def test_grant_str():
    grant = Grant.objects.create(
        title="AI for Education", funder="Kemdikbud", start_date="2024-01-01"
    )
    assert str(grant) == "AI for Education"


@pytest.mark.django_db
def test_grant_defaults():
    grant = Grant.objects.create(title="Basic Grant", funder="RISTEK", start_date="2024-01-01")
    assert grant.currency == "IDR"
    assert grant.role == Grant.Role.MEMBER
    assert grant.status == Grant.Status.PROPOSED
    assert grant.is_public is False
