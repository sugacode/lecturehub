from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


@login_required
def document_list(request: HttpRequest) -> HttpResponse:
    """Document vault list (filled in Phase 2)."""
    return render(request, "placeholder.html", {"title": "Documents"})
