import secrets

from django.conf import settings
from django.db import models


def generate_public_slug() -> str:
    return secrets.token_urlsafe(9)[:12]


class Profile(models.Model):
    """Extended profile for a lecturer, one-to-one with the auth User."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )

    full_name = models.CharField(max_length=200)
    title_prefix = models.CharField(max_length=30, blank=True, help_text='e.g. "Dr."')
    title_suffix = models.CharField(max_length=60, blank=True, help_text='e.g. "M.Kom"')

    nidn = models.CharField("NIDN", max_length=30, blank=True)
    nip = models.CharField("NIP", max_length=30, blank=True)
    orcid = models.CharField("ORCID", max_length=50, blank=True)
    scopus_id = models.CharField("Scopus ID", max_length=50, blank=True)
    sinta_id = models.CharField("SINTA ID", max_length=50, blank=True)
    google_scholar_id = models.CharField("Google Scholar ID", max_length=50, blank=True)

    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    photo = models.ImageField(upload_to="profile/", blank=True, null=True)
    bio = models.TextField(blank=True)

    institution = models.CharField(max_length=200, blank=True)
    faculty = models.CharField(max_length=200, blank=True)
    department = models.CharField(max_length=200, blank=True)
    current_position = models.CharField(max_length=200, blank=True)

    linkedin_url = models.URLField(blank=True)
    personal_website = models.URLField(blank=True)

    public_email = models.EmailField(blank=True, help_text="Email shown on the public CV page")
    show_phone_publicly = models.BooleanField(default=False)
    public_slug = models.CharField(
        max_length=12, unique=True, default=generate_public_slug, editable=False
    )

    def __str__(self) -> str:
        return f"{self.title_prefix} {self.full_name} {self.title_suffix}".strip()

    def regenerate_public_slug(self) -> None:
        self.public_slug = generate_public_slug()
        self.save(update_fields=["public_slug"])
