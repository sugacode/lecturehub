import datetime

from django.conf import settings
from django.core.cache import cache
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from apps.accounts.models import Profile
from apps.cv.pdf_data import get_cv_context
from apps.schedule.models import Event, Semester, TeachingAssignment

WEEKDAY_LABELS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

REALIZE_KEYS = [
    "educations",
    "positions",
    "achievements",
    "skills",
    "trainings",
    "intellectual_properties",
    "grants",
    "community_services",
    "organizational_roles",
]


def _check_public_access(slug: str | None) -> None:
    """Enforce PUBLIC_PAGES_MODE: in 'unlisted' mode the slug must match the profile's."""
    if settings.PUBLIC_PAGES_MODE == "unlisted":
        profile = Profile.objects.first()
        if not profile or not slug or slug != profile.public_slug:
            raise Http404


def _apply_noindex(response: HttpResponse) -> HttpResponse:
    if settings.PUBLIC_PAGES_MODE == "unlisted":
        response["X-Robots-Tag"] = "noindex"
    return response


def get_cached_public_cv_context() -> dict:
    """The is_public=True CV dataset, shared by the full public CV page and the
    front-page landing resume so both stay consistent and share one cache entry."""
    context = cache.get("public_cv_context")
    if context is None:
        context = get_cv_context(public_only=True)
        for key in REALIZE_KEYS:
            context[key] = list(context[key])
        cache.set("public_cv_context", context, 300)
    return context


def public_cv(request: HttpRequest, slug: str | None = None) -> HttpResponse:
    """Public, unauthenticated CV page showing only is_public=True records."""
    _check_public_access(slug)

    context = get_cached_public_cv_context()
    publications_by_type = context["publications_by_type"]
    years = sorted(
        {pub.year for _, group in publications_by_type for pub in group}, reverse=True
    )
    indexing_seen = {}
    for _, group in publications_by_type:
        for pub in group:
            indexing_seen[pub.indexing] = pub.get_indexing_display()
    all_publications = sorted(
        (pub for _, group in publications_by_type for pub in group),
        key=lambda pub: (-pub.year, pub.title),
    )
    context = {
        **context,
        "publication_years": years,
        "pub_type_choices": [(group[0].pub_type, label) for label, group in publications_by_type],
        "indexing_choices": sorted(indexing_seen.items()),
        "all_publications": all_publications,
    }
    response = render(request, "public/cv.html", context)
    return _apply_noindex(response)


def build_public_week_context() -> dict:
    """This week's public teaching assignments + public/busy events, grouped by day.

    Shared by the full public schedule page and the front-page landing resume, so
    both stay in sync on what "public" means here: never notes, meeting URLs, or
    student counts.
    """
    semester = Semester.objects.filter(is_active=True).first()
    if semester:
        assignments = TeachingAssignment.objects.filter(
            semester=semester, is_public=True
        ).select_related("course")
    else:
        assignments = TeachingAssignment.objects.none()

    today = timezone.localdate()
    monday = today - datetime.timedelta(days=today.weekday())
    saturday = monday + datetime.timedelta(days=5)
    events = Event.objects.filter(
        visibility__in=[Event.Visibility.PUBLIC, Event.Visibility.BUSY],
        start_datetime__date__range=[monday, saturday],
    )

    days = []
    for i in range(6):
        day_date = monday + datetime.timedelta(days=i)
        items = []
        for assignment in assignments.filter(day_of_week=i):
            items.append(
                {
                    "start": assignment.start_time,
                    "end": assignment.end_time,
                    "label": f"{assignment.course.code} {assignment.class_label}",
                    "sublabel": assignment.room,
                }
            )
        for event in events.filter(start_datetime__date=day_date):
            is_busy = event.visibility == Event.Visibility.BUSY
            items.append(
                {
                    "start": event.start_datetime.time(),
                    "end": event.end_datetime.time(),
                    "label": "Busy" if is_busy else event.title,
                    "sublabel": "" if is_busy else event.location,
                }
            )
        items.sort(key=lambda item: item["start"])
        days.append({"date": day_date, "label": WEEKDAY_LABELS[i], "items": items})

    return {"days": days, "semester": semester}


def public_schedule(request: HttpRequest, slug: str | None = None) -> HttpResponse:
    """Public, read-only weekly calendar: public teaching assignments + public/busy events.

    Never renders notes, meeting URLs, or student counts.
    """
    _check_public_access(slug)
    response = render(request, "public/schedule.html", build_public_week_context())
    return _apply_noindex(response)
