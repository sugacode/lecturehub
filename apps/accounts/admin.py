from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "current_position", "institution", "email")
    search_fields = ("full_name", "email", "nidn", "nip", "institution")
    list_filter = ("institution", "faculty")
