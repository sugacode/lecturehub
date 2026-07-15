from django.db import models


class CommunityService(models.Model):
    """A community service activity (pengabdian kepada masyarakat)."""

    title = models.CharField(max_length=500)
    partner = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    date = models.DateField()
    funding_source = models.CharField(max_length=255, blank=True)
    output = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Community service"

    def __str__(self) -> str:
        return self.title


class OrganizationalRole(models.Model):
    """A role in a professional or academic organization (e.g. ICMI, APSI PTMA)."""

    organization = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True, help_text="Leave blank if current")
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self) -> str:
        return f"{self.role}, {self.organization}"

    @property
    def is_current(self) -> bool:
        return self.end_date is None
