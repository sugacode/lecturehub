import pytest
from django.contrib.auth import get_user_model


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(username="lecturer", password="pass12345")


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client
