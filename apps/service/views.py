from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


@login_required
def community_service_list(request: HttpRequest) -> HttpResponse:
    """Community service list (filled in Phase 6)."""
    return render(request, "placeholder.html", {"title": "Service"})
