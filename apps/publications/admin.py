from django.contrib import admin

from .models import IntellectualProperty, Publication


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ("title", "pub_type", "venue", "year", "indexing", "citation_count")
    list_filter = ("pub_type", "indexing", "year")
    search_fields = ("title", "authors", "venue", "doi")


@admin.register(IntellectualProperty)
class IntellectualPropertyAdmin(admin.ModelAdmin):
    list_display = ("title", "ip_type", "registration_number", "registration_date")
    list_filter = ("ip_type",)
    search_fields = ("title", "registration_number")
