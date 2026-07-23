from django.urls import path

from . import views

app_name = "documents"

urlpatterns = [
    path("", views.DocumentListView.as_view(), name="document_list"),
    path("new/", views.DocumentCreateView.as_view(), name="document_create"),
    path("<int:pk>/edit/", views.DocumentUpdateView.as_view(), name="document_update"),
    path("<int:pk>/delete/", views.DocumentDeleteView.as_view(), name="document_delete"),
    path("links/", views.SharedLinkListView.as_view(), name="shared_link_list"),
    path("links/new/", views.SharedLinkCreateView.as_view(), name="shared_link_create"),
    path(
        "links/<int:pk>/edit/", views.SharedLinkUpdateView.as_view(), name="shared_link_update"
    ),
    path(
        "links/<int:pk>/delete/", views.SharedLinkDeleteView.as_view(), name="shared_link_delete"
    ),
]
