from django.db import models

from apps.documents.models import Document


class Education(models.Model):
    """A degree/qualification earned by the lecturer."""

    class DegreeLevel(models.TextChoices):
        D3 = "d3", "D3"
        S1 = "s1", "S1"
        S2 = "s2", "S2"
        S3 = "s3", "S3"
        POSTDOC = "postdoc", "Postdoc"

    degree_level = models.CharField(max_length=10, choices=DegreeLevel.choices)
    institution = models.CharField(max_length=255)
    program = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField(blank=True, null=True)
    thesis_title = models.CharField(max_length=500, blank=True)
    gpa = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    is_public = models.BooleanField(default=False)

    class Meta:
        ordering = ["-start_year"]

    def __str__(self) -> str:
        return f"{self.get_degree_level_display()} - {self.program}, {self.institution}"


class Position(models.Model):
    """A structural, functional, organizational, or professional position held."""

    class Category(models.TextChoices):
        STRUCTURAL = "structural", "Structural"
        FUNCTIONAL = "functional", "Functional"
        ORGANIZATIONAL = "organizational", "Organizational"
        PROFESSIONAL = "professional", "Professional"

    title = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=Category.choices)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True, help_text="Leave blank if current")
    description = models.TextField(blank=True)
    sk_document = models.ForeignKey(
        Document, on_delete=models.SET_NULL, blank=True, null=True, related_name="positions"
    )
    is_public = models.BooleanField(default=False)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self) -> str:
        return f"{self.title}, {self.organization}"

    @property
    def is_current(self) -> bool:
        return self.end_date is None


class Achievement(models.Model):
    """An award or recognition."""

    class Level(models.TextChoices):
        INSTITUTIONAL = "institutional", "Institutional"
        NATIONAL = "national", "National"
        INTERNATIONAL = "international", "International"

    title = models.CharField(max_length=255)
    issuer = models.CharField(max_length=255)
    level = models.CharField(max_length=20, choices=Level.choices)
    date = models.DateField()
    description = models.TextField(blank=True)
    certificate = models.ForeignKey(
        Document, on_delete=models.SET_NULL, blank=True, null=True, related_name="achievements"
    )
    is_public = models.BooleanField(default=False)

    class Meta:
        ordering = ["-date"]

    def __str__(self) -> str:
        return self.title


class Skill(models.Model):
    """A technical, language, or research skill with self-rated proficiency."""

    class Category(models.TextChoices):
        TECHNICAL = "technical", "Technical"
        LANGUAGE = "language", "Language"
        RESEARCH = "research", "Research"

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=Category.choices)
    proficiency = models.PositiveSmallIntegerField(help_text="1 (basic) to 5 (expert)")
    is_public = models.BooleanField(default=False)

    class Meta:
        ordering = ["category", "-proficiency"]

    def __str__(self) -> str:
        return f"{self.name} ({self.proficiency}/5)"


class TrainingCertification(models.Model):
    """A short course, workshop, or professional certification."""

    name = models.CharField(max_length=255)
    provider = models.CharField(max_length=255)
    date = models.DateField()
    expiry_date = models.DateField(blank=True, null=True)
    certificate = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="training_certifications",
    )
    is_public = models.BooleanField(default=False)

    class Meta:
        ordering = ["-date"]

    def __str__(self) -> str:
        return self.name
