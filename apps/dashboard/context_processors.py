from django.http import HttpRequest


def sidebar_context(request: HttpRequest) -> dict:
    """Expose the sidebar navigation items to every template."""
    return {
        "sidebar_items": [
            {"label": "Dashboard", "url_name": "dashboard:home", "icon": "home"},
            {"label": "Schedule", "url_name": "schedule:calendar_week", "icon": "calendar"},
            {"label": "Supervision", "url_name": "supervision:student_list", "icon": "users"},
            {"label": "Publications", "url_name": "publications:publication_list", "icon": "book"},
            {"label": "Research", "url_name": "research:grant_list", "icon": "flask"},
            {"label": "CV", "url_name": "cv:education_list", "icon": "id"},
            {"label": "Service", "url_name": "service:community_service_list", "icon": "heart"},
            {"label": "Documents", "url_name": "documents:document_list", "icon": "folder"},
            {"label": "Profile", "url_name": "accounts:profile_edit", "icon": "user"},
        ]
    }
