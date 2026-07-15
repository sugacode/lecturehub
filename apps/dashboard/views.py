from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


@login_required
def home(request: HttpRequest) -> HttpResponse:
    """Dashboard home aggregating upcoming deadlines and stats (filled in Phase 7)."""
    return render(request, "dashboard/home.html", {})


@login_required
def search(request: HttpRequest) -> HttpResponse:
    """Global search across publications, students, documents, and events (filled in Phase 7)."""
    return render(request, "placeholder.html", {"title": "Search"})
