from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


@login_required
def publication_list(request: HttpRequest) -> HttpResponse:
    """Publication list (filled in Phase 3)."""
    return render(request, "placeholder.html", {"title": "Publications"})
