from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models

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
