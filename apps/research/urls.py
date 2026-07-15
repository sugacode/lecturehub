from django.urls import path

from . import views

app_name = "research"

urlpatterns = [
    path("", views.grant_list, name="grant_list"),
]
