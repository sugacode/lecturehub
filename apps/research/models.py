from django.db import models


class Grant(models.Model):
    """A research grant. Deliverables and full CRUD UI are added in Phase 6."""

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
