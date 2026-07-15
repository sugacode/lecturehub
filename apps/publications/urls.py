from django.urls import path

from . import views

app_name = "publications"

urlpatterns = [
    path("", views.PublicationListView.as_view(), name="publication_list"),
    path("new/", views.PublicationCreateView.as_view(), name="publication_create"),
    path("import/", views.import_by_doi, name="import_by_doi"),
    path("<int:pk>/edit/", views.PublicationUpdateView.as_view(), name="publication_update"),
    path("<int:pk>/delete/", views.PublicationDeleteView.as_view(), name="publication_delete"),
    path("ip/", views.IntellectualPropertyListView.as_view(), name="ip_list"),
    path("ip/new/", views.IntellectualPropertyCreateView.as_view(), name="ip_create"),
    path("ip/<int:pk>/edit/", views.IntellectualPropertyUpdateView.as_view(), name="ip_update"),
    path("ip/<int:pk>/delete/", views.IntellectualPropertyDeleteView.as_view(), name="ip_delete"),
]
