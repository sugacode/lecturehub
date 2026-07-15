from django.urls import path

from . import views

app_name = "research"

urlpatterns = [
    path("", views.GrantListView.as_view(), name="grant_list"),
    path("new/", views.GrantCreateView.as_view(), name="grant_create"),
    path("<int:pk>/", views.grant_detail, name="grant_detail"),
    path("<int:pk>/edit/", views.GrantUpdateView.as_view(), name="grant_update"),
    path("<int:pk>/delete/", views.GrantDeleteView.as_view(), name="grant_delete"),
    path(
        "<int:grant_pk>/deliverables/new/",
        views.deliverable_create,
        name="deliverable_create",
    ),
    path(
        "deliverables/<int:pk>/edit/",
        views.DeliverableUpdateView.as_view(),
        name="deliverable_update",
    ),
    path(
        "deliverables/<int:pk>/delete/",
        views.DeliverableDeleteView.as_view(),
        name="deliverable_delete",
    ),
]
