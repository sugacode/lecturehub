import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_login_page_renders_captcha_field(client):
    response = client.get(reverse("login"))
    assert response.status_code == 200
    assert b"captcha" in response.content.lower()


@pytest.mark.django_db
def test_login_fails_without_captcha_even_with_correct_credentials(client, user):
    response = client.post(
        reverse("login"), {"username": "lecturer", "password": "pass12345"}
    )
    assert response.status_code == 200  # re-renders the form with errors, no redirect
    assert not response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_login_fails_with_wrong_captcha_response(client, user):
    response = client.post(
        reverse("login"),
        {
            "username": "lecturer",
            "password": "pass12345",
            "captcha_0": "irrelevant-hashkey",
            "captcha_1": "wrong-answer",
        },
    )
    assert response.status_code == 200
    assert not response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_login_succeeds_with_correct_credentials_and_captcha(client, user):
    """CAPTCHA_TEST_MODE (set in config/settings/test.py) accepts the fixed
    response "PASSED" for any challenge, so the real image doesn't need
    solving."""
    response = client.post(
        reverse("login"),
        {
            "username": "lecturer",
            "password": "pass12345",
            "captcha_0": "irrelevant-hashkey",
            "captcha_1": "PASSED",
        },
    )
    assert response.status_code == 302
    assert "_auth_user_id" in client.session
