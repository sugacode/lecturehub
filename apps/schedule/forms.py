from django import forms

from .models import Course, Event, Semester, TeachingAssignment


class SemesterForm(forms.ModelForm):
    class Meta:
        model = Semester
        fields = ["name", "start_date", "end_date", "is_active"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["code", "name", "credits", "program", "level"]


class TeachingAssignmentForm(forms.ModelForm):
    class Meta:
        model = TeachingAssignment
        fields = [
            "course", "semester", "class_label", "day_of_week",
            "start_time", "end_time", "room", "student_count", "is_public",
        ]
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "title", "category", "start_datetime", "end_datetime", "location",
            "is_online", "meeting_url", "notes", "related_grant", "recurrence", "visibility",
        ]
        widgets = {
            "start_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
