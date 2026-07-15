from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("profile/", views.profile_edit, name="profile_edit"),
    path("profile/regenerate-slug/", views.regenerate_slug, name="regenerate_slug"),
]
