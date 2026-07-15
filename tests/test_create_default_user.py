import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError


@pytest.mark.django_db
def test_create_default_user_from_env(monkeypatch):
    monkeypatch.setenv("DEFAULT_ADMIN_USERNAME", "owner")
    monkeypatch.setenv("DEFAULT_ADMIN_EMAIL", "owner@example.com")
    monkeypatch.setenv("DEFAULT_ADMIN_PASSWORD", "s3cret-pass")

    call_command("create_default_user")

    User = get_user_model()
    user = User.objects.get(username="owner")
    assert user.is_superuser
    assert user.check_password("s3cret-pass")
    assert hasattr(user, "profile")


@pytest.mark.django_db
def test_create_default_user_requires_env(monkeypatch):
    monkeypatch.delenv("DEFAULT_ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("DEFAULT_ADMIN_PASSWORD", raising=False)
    with pytest.raises(CommandError):
        call_command("create_default_user")
