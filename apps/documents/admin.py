from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "upload_date", "expiry_date")
    list_filter = ("category",)
    search_fields = ("title", "tags", "notes")
