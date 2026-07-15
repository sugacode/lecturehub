from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


@login_required
def grant_list(request: HttpRequest) -> HttpResponse:
    """Grant list (filled in Phase 6)."""
    return render(request, "placeholder.html", {"title": "Research"})
