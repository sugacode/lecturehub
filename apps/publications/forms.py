from django import forms

from .models import IntellectualProperty, Publication


class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = [
            "pub_type", "title", "authors", "venue", "year", "volume", "issue", "pages",
            "doi", "url", "indexing", "citation_count", "is_corresponding_author",
            "grant", "is_public",
        ]
        widgets = {
            "authors": forms.Textarea(attrs={"rows": 2}),
        }


class IntellectualPropertyForm(forms.ModelForm):
    class Meta:
        model = IntellectualProperty
        fields = [
            "title", "ip_type", "registration_number", "certificate",
            "registration_date", "description", "is_public",
        ]
        widgets = {
            "registration_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class DoiImportForm(forms.Form):
    doi = forms.CharField(
        label="DOI",
        max_length=255,
        widget=forms.TextInput(attrs={"placeholder": "10.1000/xyz123"}),
    )
