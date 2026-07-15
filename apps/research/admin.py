from django.contrib import admin

from .models import Grant


@admin.register(Grant)
class GrantAdmin(admin.ModelAdmin):
    list_display = ("title", "funder", "role", "status", "start_date", "end_date", "is_public")
    list_filter = ("status", "role", "is_public")
    search_fields = ("title", "funder", "grant_number")
