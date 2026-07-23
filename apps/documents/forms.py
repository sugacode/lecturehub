from django import forms

from .models import Document, SharedLink


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["title", "category", "file", "expiry_date", "tags", "notes"]
        widgets = {
            "expiry_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class SharedLinkForm(forms.ModelForm):
    class Meta:
        model = SharedLink
        fields = ["name", "original_url", "slug"]
        widgets = {
            "slug": forms.TextInput(
                attrs={"placeholder": "auto-generated from name if left blank"}
            ),
        }
