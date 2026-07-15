from django.urls import path

from . import views

app_name = "supervision"

urlpatterns = [
    path("", views.StudentListView.as_view(), name="student_list"),
    path("new/", views.StudentCreateView.as_view(), name="student_create"),
    path("<int:pk>/edit/", views.StudentUpdateView.as_view(), name="student_update"),
    path("<int:pk>/delete/", views.StudentDeleteView.as_view(), name="student_delete"),
    path("<int:pk>/", views.student_timeline, name="student_timeline"),
    path(
        "<int:student_pk>/milestones/new/", views.milestone_create, name="milestone_create"
    ),
    path(
        "milestones/<int:pk>/delete/",
        views.MilestoneDeleteView.as_view(),
        name="milestone_delete",
    ),
    path("<int:student_pk>/logs/new/", views.log_create, name="log_create"),
    path(
        "logs/<int:pk>/delete/",
        views.SupervisionLogDeleteView.as_view(),
        name="log_delete",
    ),
]
