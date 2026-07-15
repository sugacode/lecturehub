from django.contrib import admin

from .models import Deliverable, Grant


class DeliverableInline(admin.TabularInline):
    model = Deliverable
    extra = 0


@admin.register(Grant)
class GrantAdmin(admin.ModelAdmin):
    list_display = ("title", "funder", "role", "status", "start_date", "end_date", "is_public")
    list_filter = ("status", "role", "is_public")
    search_fields = ("title", "funder", "grant_number")
    inlines = [DeliverableInline]


@admin.register(Deliverable)
class DeliverableAdmin(admin.ModelAdmin):
    list_display = ("name", "grant", "type", "due_date", "completed")
    list_filter = ("type", "completed")
    search_fields = ("name", "grant__title")
