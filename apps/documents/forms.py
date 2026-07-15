from django import forms

from .models import Document


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["title", "category", "file", "expiry_date", "tags", "notes"]
        widgets = {
            "expiry_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
