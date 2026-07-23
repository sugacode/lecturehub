from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.text import slugify

MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024


def validate_file_size(value) -> None:
    if value.size > MAX_UPLOAD_SIZE_BYTES:
        raise ValidationError("File must be 10 MB or smaller.")


class Document(models.Model):
    """A stored file in the personal document vault (SK, certificates, LoA, etc.)."""

    class Category(models.TextChoices):
        SK = "sk", "SK"
        CERTIFICATE = "certificate", "Certificate"
        LOA = "loa", "LoA"
        CONTRACT = "contract", "Contract"
        REPORT = "report", "Report"
        OTHER = "other", "Other"

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    file = models.FileField(
        upload_to="documents/%Y/%m/",
        validators=[FileExtensionValidator(["pdf", "jpg", "jpeg", "png"]), validate_file_size],
    )
    upload_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField(blank=True, null=True)
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags")
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-upload_date"]

    def __str__(self) -> str:
        return self.title

    def tag_list(self) -> list[str]:
        return [t.strip() for t in self.tags.split(",") if t.strip()]


class SharedLink(models.Model):
    """A custom-URL public redirect to any resource — a CV PDF, an uploaded
    Document, or any external link — reachable at /s/<slug>/ without login,
    the same way the public CV and Schedule pages are."""

    name = models.CharField("Name of document", max_length=255)
    original_url = models.URLField("Original URL", max_length=1000)
    slug = models.SlugField(
        max_length=80,
        unique=True,
        blank=True,
        help_text="Custom part of the share link, e.g. 'my-cv'. Auto-generated from the "
        "name if left blank.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self) -> str:
        base = slugify(self.name)[:70] or "link"
        slug = base
        suffix = 2
        while SharedLink.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base}-{suffix}"
            suffix += 1
        return slug
