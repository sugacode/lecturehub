import pytest
from django.urls import reverse

from apps.accounts.models import Profile


@pytest.mark.django_db
def test_profile_str():
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.create_user(username="jane", password="pass12345")
    profile = Profile.objects.create(
        user=user, full_name="Jane Doe", title_prefix="Dr.", title_suffix="M.Kom"
    )
    assert str(profile) == "Dr. Jane Doe M.Kom"


@pytest.mark.django_db
def test_profile_public_slug_auto_generated():
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.create_user(username="jane2", password="pass12345")
    profile = Profile.objects.create(user=user, full_name="Jane")
    assert len(profile.public_slug) == 12


@pytest.mark.django_db
def test_profile_edit_requires_login(client):
    response = client.get(reverse("accounts:profile_edit"))
    assert response.status_code == 302
    assert reverse("login") in response.url


@pytest.mark.django_db
def test_profile_edit_creates_profile_for_logged_in_user(auth_client, user):
    response = auth_client.get(reverse("accounts:profile_edit"))
    assert response.status_code == 200
    assert Profile.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_profile_edit_updates_fields(auth_client, user):
    Profile.objects.create(user=user, full_name="Old Name")
    response = auth_client.post(
        reverse("accounts:profile_edit"),
        {"full_name": "New Name", "title_prefix": "", "title_suffix": ""},
    )
    assert response.status_code == 302
    user.profile.refresh_from_db()
    assert user.profile.full_name == "New Name"


@pytest.mark.django_db
def test_regenerate_slug_changes_value(auth_client, user):
    profile = Profile.objects.create(user=user, full_name="Jane")
    old_slug = profile.public_slug
    response = auth_client.post(reverse("accounts:regenerate_slug"))
    assert response.status_code == 302
    profile.refresh_from_db()
    assert profile.public_slug != old_slug

@pytest.mark.django_db
def test_profile_external_link_properties(user):
    profile = Profile.objects.create(
        user=user,
        full_name="Jane",
        orcid="0000-0002-6456-576X",
        google_scholar_id="DRt8xy4AAAAJ",
        linkedin_url="https://www.linkedin.com/in/ahmadagussetiawan",
        phone="+62 822 4566 7731",
    )
    assert profile.orcid_url == "https://orcid.org/0000-0002-6456-576X"
    assert profile.google_scholar_url == (
        "https://scholar.google.com/citations?user=DRt8xy4AAAAJ"
    )
    assert profile.linkedin_label == "in/ahmadagussetiawan"
    assert profile.whatsapp_url == "https://wa.me/6282245667731"


@pytest.mark.django_db
def test_profile_external_link_properties_empty_when_unset(user):
    profile = Profile.objects.create(user=user, full_name="Jane")
    assert profile.orcid_url == ""
    assert profile.google_scholar_url == ""
    assert profile.linkedin_label == ""
    assert profile.whatsapp_url == ""


def test_session_expires_after_one_day():
    from django.conf import settings

    assert settings.SESSION_COOKIE_AGE == 60 * 60 * 24
