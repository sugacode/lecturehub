from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


@login_required
def student_list(request: HttpRequest) -> HttpResponse:
    """Supervised student list (filled in Phase 5)."""
    return render(request, "placeholder.html", {"title": "Supervision"})
