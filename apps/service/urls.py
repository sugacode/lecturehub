from django.urls import path

from . import views

app_name = "service"

urlpatterns = [
    path("", views.CommunityServiceListView.as_view(), name="community_service_list"),
    path("new/", views.CommunityServiceCreateView.as_view(), name="community_service_create"),
    path(
        "<int:pk>/edit/",
        views.CommunityServiceUpdateView.as_view(),
        name="community_service_update",
    ),
    path(
        "<int:pk>/delete/",
        views.CommunityServiceDeleteView.as_view(),
        name="community_service_delete",
    ),
    path("roles/", views.OrganizationalRoleListView.as_view(), name="organizational_role_list"),
    path(
        "roles/new/",
        views.OrganizationalRoleCreateView.as_view(),
        name="organizational_role_create",
    ),
    path(
        "roles/<int:pk>/edit/",
        views.OrganizationalRoleUpdateView.as_view(),
        name="organizational_role_update",
    ),
    path(
        "roles/<int:pk>/delete/",
        views.OrganizationalRoleDeleteView.as_view(),
        name="organizational_role_delete",
    ),
]
