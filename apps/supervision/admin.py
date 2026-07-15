from django.contrib import admin

from .models import Milestone, Student, SupervisionLog


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("name", "nim", "program", "level", "status", "target_defense_date")
    list_filter = ("level", "status", "program")
    search_fields = ("name", "nim", "thesis_title")


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ("name", "student", "due_date", "completed_date")
    list_filter = ("student",)
    search_fields = ("name", "student__name")


@admin.register(SupervisionLog)
class SupervisionLogAdmin(admin.ModelAdmin):
    list_display = ("student", "date", "mode")
    list_filter = ("mode", "student")
    search_fields = ("student__name", "summary")
