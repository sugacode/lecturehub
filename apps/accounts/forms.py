from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Profile


class CaptchaAuthenticationForm(AuthenticationForm):
    """Login form with an added image captcha challenge, to slow down
    automated brute-force login attempts."""

    captcha = CaptchaField()


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ["user", "public_slug"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 5}),
        }
