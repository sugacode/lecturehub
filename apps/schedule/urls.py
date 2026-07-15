from django.urls import path

from . import views

app_name = "schedule"

urlpatterns = [
    path("", views.calendar_week, name="calendar_week"),
]
