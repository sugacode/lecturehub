from django.db import models

from apps.research.models import Grant


class Semester(models.Model):
    """An academic semester, e.g. 'Ganjil 2026/2027'."""

    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self) -> str:
        return self.name


class Course(models.Model):
    """A course that can be taught across multiple semesters."""

    class Level(models.TextChoices):
        D3 = "d3", "D3"
        S1 = "s1", "S1"
        S2 = "s2", "S2"
        S3 = "s3", "S3"

    code = models.CharField(max_length=20)
    name = models.CharField(max_length=255)
    credits = models.PositiveSmallIntegerField(help_text="SKS")
    program = models.CharField(max_length=255)
    level = models.CharField(max_length=10, choices=Level.choices)

    class Meta:
        ordering = ["code"]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class TeachingAssignment(models.Model):
    """A course taught in a specific semester, on a specific day/time/room."""

    class DayOfWeek(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="assignments")
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name="assignments")
    class_label = models.CharField(max_length=50, help_text='e.g. "A", "B", "RPL"')
    day_of_week = models.IntegerField(choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=100, blank=True)
    student_count = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=False)

    class Meta:
        ordering = ["day_of_week", "start_time"]

    def __str__(self) -> str:
        return f"{self.course.code} {self.class_label} ({self.get_day_of_week_display()})"


class Event(models.Model):
    """A meeting, seminar, deadline, or other calendar event."""

    class Category(models.TextChoices):
        MEETING = "meeting", "Meeting"
        SEMINAR = "seminar", "Seminar"
        WORKSHOP = "workshop", "Workshop"
        EXAM_COMMITTEE = "exam_committee", "Exam Committee"
        GUEST_LECTURE = "guest_lecture", "Guest Lecture"
        ORGANIZATIONAL = "organizational", "Organizational"
        PERSONAL = "personal", "Personal"
        DEADLINE = "deadline", "Deadline"

    class Recurrence(models.TextChoices):
        NONE = "none", "None"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"

    class Visibility(models.TextChoices):
        PRIVATE = "private", "Private"
        BUSY = "busy", "Busy"
        PUBLIC = "public", "Public"

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=Category.choices)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True)
    is_online = models.BooleanField(default=False)
    meeting_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    related_grant = models.ForeignKey(
        Grant, on_delete=models.SET_NULL, blank=True, null=True, related_name="events"
    )
    recurrence = models.CharField(
        max_length=10, choices=Recurrence.choices, default=Recurrence.NONE
    )
    visibility = models.CharField(
        max_length=10, choices=Visibility.choices, default=Visibility.PRIVATE
    )

    class Meta:
        ordering = ["start_datetime"]

    def __str__(self) -> str:
        return self.title
