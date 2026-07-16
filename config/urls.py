"""URL configuration for the LecturerHub project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", include("apps.dashboard.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("cv/", include("apps.cv.urls")),
    path("publications/", include("apps.publications.urls")),
    path("schedule/", include("apps.schedule.urls")),
    path("supervision/", include("apps.supervision.urls")),
    path("research/", include("apps.research.urls")),
    path("service/", include("apps.service.urls")),
    path("documents/", include("apps.documents.urls")),
    path("common/", include("apps.common.urls")),
    path("p/", include("apps.dashboard.public_urls")),
]

if settings.DEBUG or settings.SERVE_MEDIA_VIA_DJANGO:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
