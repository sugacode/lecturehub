from django import forms

from .models import Milestone, Student, SupervisionLog


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "name", "nim", "program", "thesis_title", "level",
            "status", "start_date", "target_defense_date",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "target_defense_date": forms.DateInput(attrs={"type": "date"}),
            "thesis_title": forms.Textarea(attrs={"rows": 2}),
        }


class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ["name", "due_date", "completed_date", "notes"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "completed_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }


class SupervisionLogForm(forms.ModelForm):
    class Meta:
        model = SupervisionLog
        fields = ["date", "mode", "summary", "next_action"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "summary": forms.Textarea(attrs={"rows": 3}),
            "next_action": forms.Textarea(attrs={"rows": 2}),
        }
