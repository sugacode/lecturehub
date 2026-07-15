import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_dashboard_home_requires_login(client):
    response = client.get(reverse("dashboard:home"))
    assert response.status_code == 302


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
