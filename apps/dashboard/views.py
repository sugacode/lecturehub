import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from apps.documents.models import Document
from apps.publications.models import Publication
from apps.research.models import Deliverable, Grant
from apps.schedule.models import Event, Semester, TeachingAssignment
from apps.supervision.models import Milestone, Student


@login_required
def home(request: HttpRequest) -> HttpResponse:
    """Dashboard home aggregating upcoming deadlines and stats."""
    today = timezone.localdate()
    week_ahead = today + datetime.timedelta(days=7)
    month_ahead = today + datetime.timedelta(days=30)
    two_months_ahead = today + datetime.timedelta(days=60)

    upcoming_events = Event.objects.filter(start_datetime__date__range=[today, week_ahead])

    semester = Semester.objects.filter(is_active=True).first()
    upcoming_teaching = []
    if semester:
        assignments = TeachingAssignment.objects.filter(semester=semester).select_related("course")
        for offset in range(8):
            day = today + datetime.timedelta(days=offset)
            if day > week_ahead:
                break
            for assignment in assignments.filter(day_of_week=day.weekday()):
                upcoming_teaching.append({"date": day, "assignment": assignment})
    upcoming_teaching.sort(key=lambda item: (item["date"], item["assignment"].start_time))

    upcoming_deliverables = Deliverable.objects.filter(
        completed=False, due_date__range=[today, month_ahead]
    ).select_related("grant")
    upcoming_milestones = Milestone.objects.filter(
        completed_date__isnull=True, due_date__range=[today, month_ahead]
    ).select_related("student")

    publication_stats = Publication.objects.stats()

    active_grants = Grant.objects.filter(status__in=[Grant.Status.AWARDED, Grant.Status.ACTIVE])
    active_students = Student.objects.exclude(
        status__in=[Student.Status.GRADUATED, Student.Status.INACTIVE]
    )

    expiring_documents = Document.objects.filter(
        expiry_date__range=[today, two_months_ahead]
    )

    context = {
        "upcoming_events": upcoming_events,
        "upcoming_teaching": upcoming_teaching,
        "upcoming_deliverables": upcoming_deliverables,
        "upcoming_milestones": upcoming_milestones,
        "publication_stats": publication_stats,
        "active_grants": active_grants,
        "active_students": active_students,
        "expiring_documents": expiring_documents,
    }
    return render(request, "dashboard/home.html", context)


@login_required
def search(request: HttpRequest) -> HttpResponse:
    """Global search across publications, students, documents, and events."""
    query = request.GET.get("q", "").strip()
    results = {}
    if query:
        results["publications"] = Publication.objects.filter(
            Q(title__icontains=query) | Q(authors__icontains=query) | Q(venue__icontains=query)
        )
        results["students"] = Student.objects.filter(
            Q(name__icontains=query) | Q(nim__icontains=query) | Q(thesis_title__icontains=query)
        )
        results["documents"] = Document.objects.filter(
            Q(title__icontains=query) | Q(tags__icontains=query)
        )
        results["events"] = Event.objects.filter(
            Q(title__icontains=query) | Q(location__icontains=query) | Q(notes__icontains=query)
        )
    return render(request, "dashboard/search_results.html", {"query": query, "results": results})
