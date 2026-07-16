from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import ProfileForm
from .models import Profile


@login_required
def profile_edit(request: HttpRequest) -> HttpResponse:
    """Edit the single lecturer's profile, creating one if it doesn't exist yet."""
    default_name = request.user.get_full_name() or request.user.username
    profile, _ = Profile.objects.get_or_create(
        user=request.user, defaults={"full_name": default_name}
    )
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("accounts:profile_edit")
    else:
        form = ProfileForm(instance=profile)

    if settings.PUBLIC_PAGES_MODE == "unlisted":
        public_cv_url = reverse("public:public_cv_slug", args=[profile.public_slug])
        public_schedule_url = reverse("public:public_schedule_slug", args=[profile.public_slug])
    else:
        public_cv_url = reverse("public:public_cv")
        public_schedule_url = reverse("public:public_schedule")

    context = {
        "form": form,
        "profile": profile,
        "public_pages_mode": settings.PUBLIC_PAGES_MODE,
        "public_cv_url": public_cv_url,
        "public_schedule_url": public_schedule_url,
    }
    return render(request, "accounts/profile_edit.html", context)


@login_required
def regenerate_slug(request: HttpRequest) -> HttpResponse:
    """Regenerate the public unlisted-mode slug for the profile."""
    profile = request.user.profile
    if request.method == "POST":
        profile.regenerate_public_slug()
        messages.success(request, "Public link regenerated.")
    return redirect("accounts:profile_edit")
