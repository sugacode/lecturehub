from django.contrib import admin

from .models import Course, Event, Semester, TeachingAssignment


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "credits", "program", "level")
    list_filter = ("level", "program")
    search_fields = ("code", "name")


@admin.register(TeachingAssignment)
class TeachingAssignmentAdmin(admin.ModelAdmin):
    list_display = ("course", "semester", "class_label", "day_of_week", "start_time", "room")
    list_filter = ("semester", "day_of_week")
    search_fields = ("course__code", "course__name", "class_label")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "start_datetime", "end_datetime", "visibility")
    list_filter = ("category", "visibility", "recurrence")
    search_fields = ("title", "location", "notes")
