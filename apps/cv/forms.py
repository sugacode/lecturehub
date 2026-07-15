from django import forms

from .models import Achievement, Education, Position, Skill, TrainingCertification


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = [
            "degree_level", "institution", "program", "country",
            "start_year", "end_year", "thesis_title", "gpa", "is_public",
        ]


class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = [
            "title", "organization", "category", "start_date", "end_date",
            "description", "sk_document", "is_public",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class AchievementForm(forms.ModelForm):
    class Meta:
        model = Achievement
        fields = ["title", "issuer", "level", "date", "description", "certificate", "is_public"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ["name", "category", "proficiency", "is_public"]


class TrainingCertificationForm(forms.ModelForm):
    class Meta:
        model = TrainingCertification
        fields = ["name", "provider", "date", "expiry_date", "certificate", "is_public"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "expiry_date": forms.DateInput(attrs={"type": "date"}),
        }
