import json

from django.http import HttpResponse


def toast_header(message: str, level: str = "success") -> dict:
    """Build an HX-Trigger header dict that fires a client-side toast in base.html."""
    return {"HX-Trigger": json.dumps({"toast": {"message": message, "level": level}})}


def htmx_row_deleted(message: str) -> HttpResponse:
    """Empty response for an hx-delete row action: removes the row and shows a toast."""
    response = HttpResponse(status=200)
    for key, value in toast_header(message).items():
        response[key] = value
    return response
