"""Public, unauthenticated routes (/p/...)."""

from django.urls import path

from . import public_views

app_name = "public"

urlpatterns = [
    path("cv/", public_views.public_cv, name="public_cv"),
    path("cv/<str:slug>/", public_views.public_cv, name="public_cv_slug"),
    path("schedule/", public_views.public_schedule, name="public_schedule"),
    path("schedule/<str:slug>/", public_views.public_schedule, name="public_schedule_slug"),
]
