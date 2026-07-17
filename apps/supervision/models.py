from django.db import models
from django.utils import timezone


class Student(models.Model):
    """A thesis student under supervision."""

    class Level(models.TextChoices):
        D3 = "d3", "D3"
        S1 = "s1", "S1"
        S2 = "s2", "S2"
        S3 = "s3", "S3"

    class Status(models.TextChoices):
        PROPOSAL = "proposal", "Proposal"
        IN_PROGRESS = "in_progress", "In Progress"
        SEMINAR = "seminar", "Seminar"
        DEFENDED = "defended", "Defended"
        GRADUATED = "graduated", "Graduated"
        INACTIVE = "inactive", "Inactive"

    name = models.CharField(max_length=255)
    nim = models.CharField("NIM", max_length=50)
    program = models.CharField(max_length=255)
    thesis_title = models.CharField(max_length=500, blank=True)
    level = models.CharField(max_length=10, choices=Level.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PROPOSAL)
    start_date = models.DateField()
    target_defense_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.nim})"

    @property
    def is_active(self) -> bool:
        return self.status not in (self.Status.GRADUATED, self.Status.INACTIVE)

    @property
    def overdue_milestone_count(self) -> int:
        return self.milestones.filter(
            completed_date__isnull=True, due_date__lt=timezone.localdate()
        ).count()


class Milestone(models.Model):
    """A tracked step in a student's thesis progress (proposal seminar, draft chapter, etc.)."""

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="milestones")
    name = models.CharField(max_length=255)
    due_date = models.DateField()
    completed_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["due_date"]

    def __str__(self) -> str:
        return f"{self.name} ({self.student.name})"

    @property
    def is_overdue(self) -> bool:
        return self.completed_date is None and self.due_date < timezone.localdate()


class SupervisionLog(models.Model):
    """A record of a supervision meeting with a student."""

    class Mode(models.TextChoices):
        IN_PERSON = "in_person", "In Person"
        ONLINE = "online", "Online"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="logs")
    date = models.DateField()
    mode = models.CharField(max_length=10, choices=Mode.choices)
    summary = models.TextField()
    next_action = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self) -> str:
        return f"{self.student.name} - {self.date}"
