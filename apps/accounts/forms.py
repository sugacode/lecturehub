from django import forms

from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ["user", "public_slug"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 5}),
        }
