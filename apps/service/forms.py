from django import forms

from .models import CommunityService, OrganizationalRole


class CommunityServiceForm(forms.ModelForm):
    class Meta:
        model = CommunityService
        fields = [
            "title", "partner", "location", "date",
            "funding_source", "output", "description", "is_public",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class OrganizationalRoleForm(forms.ModelForm):
    class Meta:
        model = OrganizationalRole
        fields = ["organization", "role", "start_date", "end_date", "description", "is_public"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }
