import pytest
from django.core.management import call_command

from apps.publications.models import Publication
from apps.research.models import Grant
from apps.schedule.models import Course, Event, Semester
from apps.supervision.models import Student


@pytest.mark.django_db
def test_seed_demo_creates_expected_counts():
    call_command("seed_demo")
    assert Semester.objects.count() == 1
    assert Course.objects.count() == 3
    assert Publication.objects.count() == 5
    assert Grant.objects.count() == 2
    assert Student.objects.count() == 3
    assert Event.objects.count() == 4


@pytest.mark.django_db
def test_seed_demo_is_idempotent():
    call_command("seed_demo")
    call_command("seed_demo")
    assert Semester.objects.count() == 1
    assert Course.objects.count() == 3
    assert Publication.objects.count() == 5
    assert Grant.objects.count() == 2
    assert Student.objects.count() == 3
