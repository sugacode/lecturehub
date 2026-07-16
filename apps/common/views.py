from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .htmx import toast_header

ALLOWED_PUBLIC_TOGGLE_MODELS = {
    ("cv", "education"),
    ("cv", "position"),
    ("cv", "achievement"),
    ("cv", "skill"),
    ("cv", "trainingcertification"),
    ("publications", "publication"),
    ("publications", "intellectualproperty"),
    ("research", "grant"),
    ("service", "communityservice"),
    ("service", "organizationalrole"),
    ("schedule", "teachingassignment"),
}


def _get_toggleable_model(app_label: str, model_name: str):
    if (app_label, model_name) not in ALLOWED_PUBLIC_TOGGLE_MODELS:
        raise Http404("Not a toggleable model.")
    return apps.get_model(app_label, model_name)


@login_required
@require_POST
def toggle_public(request: HttpRequest, app_label: str, model_name: str, pk: int) -> HttpResponse:
    """HTMX PATCH-style toggle of is_public for a single row, used on every admin list page."""
    model = _get_toggleable_model(app_label, model_name)
    obj = get_object_or_404(model, pk=pk)
    obj.is_public = not obj.is_public
    obj.save(update_fields=["is_public"])
    response = render(
        request,
        "common/_public_toggle.html",
        {"obj": obj, "app_label": app_label, "model_name": model_name},
    )
    message = "Made public." if obj.is_public else "Made private."
    for key, value in toast_header(message).items():
        response[key] = value
    return response


@login_required
@require_POST
def bulk_make_public(request: HttpRequest, app_label: str, model_name: str) -> HttpResponse:
    """Bulk 'make public' action for the selected rows on an admin list page."""
    model = _get_toggleable_model(app_label, model_name)
    ids = request.POST.getlist("selected")
    updated = model.objects.filter(pk__in=ids).update(is_public=True)
    messages.success(request, f"Marked {updated} record(s) as public.")
    return redirect(request.POST.get("next") or "/")
