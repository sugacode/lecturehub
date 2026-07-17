import pytest
from django.core.cache import cache
from django.urls import reverse

from apps.accounts.models import Profile


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.mark.django_db
def test_dashboard_home_shows_landing_for_anonymous(client):
    response = client.get(reverse("dashboard:home"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_landing_shows_profile_and_no_login_link(client, user):
    Profile.objects.create(user=user, full_name="Jane Doe", current_position="Lecturer")
    response = client.get(reverse("dashboard:home"))
    content = response.content.decode()
    assert "Jane Doe" in content
    assert 'href="/login/"' not in content
    assert reverse("login") not in content


@pytest.mark.django_db
def test_landing_shows_this_week_schedule_section(client):
    response = client.get(reverse("dashboard:home"))
    assert b"This Week" in response.content


@pytest.mark.django_db
def test_landing_links_to_full_cv_and_schedule(client):
    response = client.get(reverse("dashboard:home"))
    content = response.content.decode()
    assert reverse("public:public_cv") in content
    assert reverse("public:public_schedule") in content


@pytest.mark.django_db
def test_dashboard_home_renders_for_logged_in_user(auth_client):
    response = auth_client.get(reverse("dashboard:home"))
    assert response.status_code == 200
    assert b"Dashboard" in response.content


@pytest.mark.django_db
def test_sidebar_links_render_without_error(auth_client):
    response = auth_client.get(reverse("dashboard:home"))
    names = [
        "Schedule", "Supervision", "Publications", "Research",
        "CV", "Service", "Documents", "Profile",
    ]
    for name in names:
        assert name.encode() in response.content
