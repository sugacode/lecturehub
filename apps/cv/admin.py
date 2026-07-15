from django.contrib import admin

from .models import Achievement, Education, Position, Skill, TrainingCertification


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ("program", "institution", "degree_level", "start_year", "end_year", "is_public")
    list_filter = ("degree_level", "is_public")
    search_fields = ("institution", "program", "thesis_title")


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("title", "organization", "category", "start_date", "end_date", "is_public")
    list_filter = ("category", "is_public")
    search_fields = ("title", "organization")


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ("title", "issuer", "level", "date", "is_public")
    list_filter = ("level", "is_public")
    search_fields = ("title", "issuer")


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "proficiency", "is_public")
    list_filter = ("category", "is_public")
    search_fields = ("name",)


@admin.register(TrainingCertification)
class TrainingCertificationAdmin(admin.ModelAdmin):
    list_display = ("name", "provider", "date", "expiry_date", "is_public")
    list_filter = ("is_public",)
    search_fields = ("name", "provider")
