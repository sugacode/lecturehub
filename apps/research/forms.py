from django import forms

from .models import Deliverable, Grant


class GrantForm(forms.ModelForm):
    class Meta:
        model = Grant
        fields = [
            "title", "funder", "grant_number", "scheme", "role", "amount",
            "currency", "start_date", "end_date", "status", "is_public",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }


class DeliverableForm(forms.ModelForm):
    class Meta:
        model = Deliverable
        fields = ["name", "type", "due_date", "completed", "document"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }
