from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


@login_required
def calendar_week(request: HttpRequest) -> HttpResponse:
    """Weekly calendar view (filled in Phase 4)."""
    return render(request, "placeholder.html", {"title": "Schedule"})
