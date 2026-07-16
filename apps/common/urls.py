from django.urls import path

from . import views

app_name = "common"

urlpatterns = [
    path(
        "toggle-public/<str:app_label>/<str:model_name>/<int:pk>/",
        views.toggle_public,
        name="toggle_public",
    ),
    path(
        "bulk-make-public/<str:app_label>/<str:model_name>/",
        views.bulk_make_public,
        name="bulk_make_public",
    ),
]
