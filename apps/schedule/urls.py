from django.urls import path

from . import views

app_name = "schedule"

urlpatterns = [
    path("", views.calendar_week, name="calendar_week"),
    path("month/", views.calendar_month, name="calendar_month"),
    path("export.ics", views.export_ics, name="export_ics"),
    path("semesters/", views.SemesterListView.as_view(), name="semester_list"),
    path("semesters/new/", views.SemesterCreateView.as_view(), name="semester_create"),
    path(
        "semesters/<int:pk>/edit/", views.SemesterUpdateView.as_view(), name="semester_update"
    ),
    path(
        "semesters/<int:pk>/delete/", views.SemesterDeleteView.as_view(), name="semester_delete"
    ),
    path("courses/", views.CourseListView.as_view(), name="course_list"),
    path("courses/new/", views.CourseCreateView.as_view(), name="course_create"),
    path("courses/<int:pk>/edit/", views.CourseUpdateView.as_view(), name="course_update"),
    path("courses/<int:pk>/delete/", views.CourseDeleteView.as_view(), name="course_delete"),
    path("assignments/", views.TeachingAssignmentListView.as_view(), name="assignment_list"),
    path(
        "assignments/new/",
        views.TeachingAssignmentCreateView.as_view(),
        name="assignment_create",
    ),
    path(
        "assignments/<int:pk>/edit/",
        views.TeachingAssignmentUpdateView.as_view(),
        name="assignment_update",
    ),
    path(
        "assignments/<int:pk>/delete/",
        views.TeachingAssignmentDeleteView.as_view(),
        name="assignment_delete",
    ),
    path("events/", views.EventListView.as_view(), name="event_list"),
    path("events/new/", views.EventCreateView.as_view(), name="event_create"),
    path("events/<int:pk>/edit/", views.EventUpdateView.as_view(), name="event_update"),
    path("events/<int:pk>/delete/", views.EventDeleteView.as_view(), name="event_delete"),
]
