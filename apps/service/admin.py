from django.contrib import admin

from .models import CommunityService, OrganizationalRole


@admin.register(CommunityService)
class CommunityServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "partner", "location", "date", "is_public")
    list_filter = ("is_public",)
    search_fields = ("title", "partner", "location", "output")


@admin.register(OrganizationalRole)
class OrganizationalRoleAdmin(admin.ModelAdmin):
    list_display = ("role", "organization", "start_date", "end_date", "is_public")
    list_filter = ("is_public",)
    search_fields = ("role", "organization")
