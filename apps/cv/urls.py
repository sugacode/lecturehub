from django.urls import path

from . import views

app_name = "cv"

urlpatterns = [
    path("export/", views.cv_export, name="export"),
    path("", views.EducationListView.as_view(), name="education_list"),
    path("education/new/", views.EducationCreateView.as_view(), name="education_create"),
    path(
        "education/<int:pk>/edit/",
        views.EducationUpdateView.as_view(),
        name="education_update",
    ),
    path(
        "education/<int:pk>/delete/",
        views.EducationDeleteView.as_view(),
        name="education_delete",
    ),
    path("positions/", views.PositionListView.as_view(), name="position_list"),
    path("positions/new/", views.PositionCreateView.as_view(), name="position_create"),
    path("positions/<int:pk>/edit/", views.PositionUpdateView.as_view(), name="position_update"),
    path("positions/<int:pk>/delete/", views.PositionDeleteView.as_view(), name="position_delete"),
    path("achievements/", views.AchievementListView.as_view(), name="achievement_list"),
    path("achievements/new/", views.AchievementCreateView.as_view(), name="achievement_create"),
    path(
        "achievements/<int:pk>/edit/",
        views.AchievementUpdateView.as_view(),
        name="achievement_update",
    ),
    path(
        "achievements/<int:pk>/delete/",
        views.AchievementDeleteView.as_view(),
        name="achievement_delete",
    ),
    path("skills/", views.SkillListView.as_view(), name="skill_list"),
    path("skills/new/", views.SkillCreateView.as_view(), name="skill_create"),
    path("skills/<int:pk>/edit/", views.SkillUpdateView.as_view(), name="skill_update"),
    path("skills/<int:pk>/delete/", views.SkillDeleteView.as_view(), name="skill_delete"),
    path("training/", views.TrainingCertificationListView.as_view(), name="training_list"),
    path("training/new/", views.TrainingCertificationCreateView.as_view(), name="training_create"),
    path(
        "training/<int:pk>/edit/",
        views.TrainingCertificationUpdateView.as_view(),
        name="training_update",
    ),
    path(
        "training/<int:pk>/delete/",
        views.TrainingCertificationDeleteView.as_view(),
        name="training_delete",
    ),
]
