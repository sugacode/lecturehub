from django.db import models

from apps.documents.models import Document


class Grant(models.Model):
    """A research grant with role, funding, and lifecycle status."""

    class Role(models.TextChoices):
        PI = "pi", "PI"
        CO_PI = "co_pi", "Co-PI"
        MEMBER = "member", "Member"

    class Status(models.TextChoices):
        PROPOSED = "proposed", "Proposed"
        AWARDED = "awarded", "Awarded"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        REJECTED = "rejected", "Rejected"

    title = models.CharField(max_length=500)
    funder = models.CharField(max_length=255)
    grant_number = models.CharField(max_length=100, blank=True)
    scheme = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=10, default="IDR")
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PROPOSED)
    is_public = models.BooleanField(default=False)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self) -> str:
        return self.title

    @property
    def is_active(self) -> bool:
        return self.status in (self.Status.AWARDED, self.Status.ACTIVE)


class Deliverable(models.Model):
    """A required output of a grant (report, publication, prototype, or IP)."""

    class DeliverableType(models.TextChoices):
        REPORT = "report", "Report"
        PUBLICATION = "publication", "Publication"
        PROTOTYPE = "prototype", "Prototype"
        IP = "ip", "Intellectual Property"

    grant = models.ForeignKey(Grant, on_delete=models.CASCADE, related_name="deliverables")
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=DeliverableType.choices)
    due_date = models.DateField()
    completed = models.BooleanField(default=False)
    document = models.ForeignKey(
        Document, on_delete=models.SET_NULL, blank=True, null=True, related_name="deliverables"
    )

    class Meta:
        ordering = ["due_date"]

    def __str__(self) -> str:
        return f"{self.name} ({self.grant.title})"
