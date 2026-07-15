from django.urls import path

from . import views

app_name = "service"

urlpatterns = [
    path("", views.community_service_list, name="community_service_list"),
]
