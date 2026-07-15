from django.db import models
from django.db.models import Count

from apps.documents.models import Document
from apps.research.models import Grant


class PublicationManager(models.Manager):
    """Adds aggregate stats used by the dashboard and CV export."""

    def stats(self) -> dict:
        qs = self.get_queryset()
        return {
            "total": qs.count(),
            "by_type": dict(qs.values_list("pub_type").annotate(count=Count("id")).order_by()),
            "by_indexing": dict(
                qs.values_list("indexing").annotate(count=Count("id")).order_by()
            ),
            "by_year": dict(
                qs.values_list("year").annotate(count=Count("id")).order_by("-year")
            ),
        }


class Publication(models.Model):
    """A journal article, conference paper, book, or book chapter."""

    class PubType(models.TextChoices):
        JOURNAL_ARTICLE = "journal_article", "Journal Article"
        CONFERENCE_PAPER = "conference_paper", "Conference Paper"
        BOOK = "book", "Book"
        BOOK_CHAPTER = "book_chapter", "Book Chapter"

    class Indexing(models.TextChoices):
        SCOPUS_Q1 = "scopus_q1", "Scopus Q1"
        SCOPUS_Q2 = "scopus_q2", "Scopus Q2"
        SCOPUS_Q3 = "scopus_q3", "Scopus Q3"
        SCOPUS_Q4 = "scopus_q4", "Scopus Q4"
        WOS = "wos", "Web of Science"
        SINTA_1 = "sinta_1", "SINTA 1"
        SINTA_2 = "sinta_2", "SINTA 2"
        SINTA_3 = "sinta_3", "SINTA 3"
        SINTA_4 = "sinta_4", "SINTA 4"
        SINTA_5 = "sinta_5", "SINTA 5"
        SINTA_6 = "sinta_6", "SINTA 6"
        OTHER = "other", "Other"
        NONE = "none", "None"

    pub_type = models.CharField(max_length=20, choices=PubType.choices)
    title = models.CharField(max_length=500)
    authors = models.TextField(help_text="Author list in citation order")
    venue = models.CharField(max_length=500, help_text="Journal, conference, or publisher name")
    year = models.PositiveIntegerField()
    volume = models.CharField(max_length=50, blank=True)
    issue = models.CharField(max_length=50, blank=True)
    pages = models.CharField(max_length=50, blank=True)
    doi = models.CharField("DOI", max_length=255, blank=True)
    url = models.URLField(blank=True)
    indexing = models.CharField(max_length=20, choices=Indexing.choices, default=Indexing.NONE)
    citation_count = models.PositiveIntegerField(default=0)
    is_corresponding_author = models.BooleanField(default=False)
    grant = models.ForeignKey(
        Grant, on_delete=models.SET_NULL, blank=True, null=True, related_name="publications"
    )
    is_public = models.BooleanField(default=False)

    objects = PublicationManager()

    class Meta:
        ordering = ["-year", "title"]

    def __str__(self) -> str:
        return f"{self.title} ({self.year})"


class IntellectualProperty(models.Model):
    """A copyright, patent, or trademark registered with DJKI."""

    class IpType(models.TextChoices):
        COPYRIGHT = "copyright", "Copyright"
        PATENT = "patent", "Patent"
        TRADEMARK = "trademark", "Trademark"

    title = models.CharField(max_length=500)
    ip_type = models.CharField(max_length=20, choices=IpType.choices)
    registration_number = models.CharField(max_length=100, blank=True)
    certificate = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="intellectual_properties",
    )
    registration_date = models.DateField()
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)

    class Meta:
        ordering = ["-registration_date"]
        verbose_name_plural = "Intellectual property"

    def __str__(self) -> str:
        return self.title
