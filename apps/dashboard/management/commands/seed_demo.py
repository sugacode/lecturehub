import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.cv.models import Achievement, Education, Position, Skill
from apps.publications.models import Publication
from apps.research.models import Grant
from apps.schedule.models import Course, Event, Semester, TeachingAssignment
from apps.service.models import CommunityService, OrganizationalRole
from apps.supervision.models import Milestone, Student, SupervisionLog


class Command(BaseCommand):
    """Seed a handful of demo records so the app looks alive on first run."""

    help = (
        "Create one semester, three courses, five publications, "
        "two grants, three students, and events."
    )

    def handle(self, *args, **options) -> None:
        today = timezone.localdate()

        semester, _ = Semester.objects.get_or_create(
            name="Ganjil 2026/2027",
            defaults={
                "start_date": today - datetime.timedelta(days=30),
                "end_date": today + datetime.timedelta(days=120),
                "is_active": True,
            },
        )

        courses_data = [
            ("IF301", "Web Programming", 3, "Information Systems", "s1"),
            ("IF302", "Human-Computer Interaction", 3, "Information Systems", "s1"),
            ("IF501", "Advanced Software Engineering", 3, "Information Systems", "s2"),
        ]
        courses = []
        for code, name, credits, program, level in courses_data:
            course, _ = Course.objects.get_or_create(
                code=code,
                defaults={"name": name, "credits": credits, "program": program, "level": level},
            )
            courses.append(course)

        assignment_slots = [
            (0, datetime.time(8, 0), datetime.time(10, 0), "Lab 3"),
            (1, datetime.time(10, 0), datetime.time(12, 0), "Room 201"),
            (3, datetime.time(13, 0), datetime.time(15, 0), "Room 305"),
        ]
        for course, (day, start, end, room) in zip(courses, assignment_slots):
            TeachingAssignment.objects.get_or_create(
                course=course,
                semester=semester,
                class_label="A",
                defaults={
                    "day_of_week": day,
                    "start_time": start,
                    "end_time": end,
                    "room": room,
                    "student_count": 35,
                    "is_public": True,
                },
            )

        publications_data = [
            (
                "journal_article",
                "Adaptive UI Personalization Using Behavioral Signals",
                "Setiawan, A., Sukmasetya, P.",
                "Journal of Human-Computer Studies",
                2025,
                "scopus_q2",
            ),
            (
                "journal_article",
                "Usability Evaluation of University Academic Information Systems",
                "Setiawan, A., Arumi, E. R.",
                "Journal of Engineering Science and Technology",
                2023,
                "scopus_q3",
            ),
            (
                "conference_paper",
                "UI/UX Design of an E-Catalog Website Using Design Thinking",
                "Falalanggi, B., Setiawan, A.",
                "BIS Information Technology and Computer Science",
                2024,
                "other",
            ),
            (
                "conference_paper",
                "Task Analysis of Frequently Used Social Media Menus",
                "Setiawan, A.",
                "Journal of Physics: Conference Series",
                2019,
                "sinta_2",
            ),
            (
                "book",
                "Personalisasi Antarmuka Berbasis AI",
                "Setiawan, A., Sukmasetya, P.",
                "UNIMMA Press",
                2024,
                "none",
            ),
        ]
        for pub_type, title, authors, venue, year, indexing in publications_data:
            Publication.objects.get_or_create(
                title=title,
                defaults={
                    "pub_type": pub_type,
                    "authors": authors,
                    "venue": venue,
                    "year": year,
                    "indexing": indexing,
                    "is_public": True,
                },
            )

        grants_data = [
            ("AI-Assisted Learning Analytics", "Kemdikbudristek", "pi", "active"),
            (
                "Adaptive UI Design for Higher Education",
                "Ministry of Higher Education",
                "co_pi",
                "completed",
            ),
        ]
        grants = []
        for title, funder, role, status in grants_data:
            grant, _ = Grant.objects.get_or_create(
                title=title,
                defaults={
                    "funder": funder,
                    "role": role,
                    "status": status,
                    "start_date": today - datetime.timedelta(days=200),
                    "end_date": today + datetime.timedelta(days=100),
                    "is_public": True,
                },
            )
            grants.append(grant)

        students_data = [
            ("Siti Rahma", "1301210001", "s1", "proposal"),
            ("Budi Santoso", "1301210002", "s1", "in_progress"),
            ("Dewi Anggraini", "2201210010", "s2", "seminar"),
        ]
        for name, nim, level, status in students_data:
            student, _ = Student.objects.get_or_create(
                nim=nim,
                defaults={
                    "name": name,
                    "program": "Information Systems",
                    "level": level,
                    "status": status,
                    "start_date": today - datetime.timedelta(days=180),
                    "target_defense_date": today + datetime.timedelta(days=90),
                },
            )
            Milestone.objects.get_or_create(
                student=student,
                name="Proposal Seminar",
                defaults={"due_date": today + datetime.timedelta(days=14)},
            )
            SupervisionLog.objects.get_or_create(
                student=student,
                date=today - datetime.timedelta(days=7),
                defaults={
                    "mode": "in_person",
                    "summary": "Discussed research direction and next steps.",
                },
            )

        events_data = [
            ("Faculty Senate Meeting", "meeting", 2, 9, 11, "Meeting Hall"),
            ("Guest Lecture: AI in Education", "guest_lecture", 4, 13, 15, "Auditorium"),
            ("Thesis Defense Committee", "exam_committee", 9, 9, 12, "Room 401"),
            ("Community Workshop Planning", "organizational", -3, 10, 11, "Online"),
        ]
        for title, category, day_offset, start_hour, end_hour, location in events_data:
            event_date = today + datetime.timedelta(days=day_offset)
            start_dt = timezone.make_aware(
                datetime.datetime.combine(event_date, datetime.time(start_hour, 0))
            )
            end_dt = timezone.make_aware(
                datetime.datetime.combine(event_date, datetime.time(end_hour, 0))
            )
            Event.objects.get_or_create(
                title=title,
                defaults={
                    "category": category,
                    "start_datetime": start_dt,
                    "end_datetime": end_dt,
                    "location": location,
                    "visibility": "public",
                },
            )

        Education.objects.get_or_create(
            institution="Universitas Gadjah Mada",
            program="Information Technology",
            defaults={
                "degree_level": "s2",
                "country": "Indonesia",
                "start_year": 2012,
                "end_year": 2014,
                "gpa": 3.33,
                "is_public": True,
            },
        )
        Position.objects.get_or_create(
            title="Head of Information System Bureau",
            organization="University",
            defaults={
                "category": "structural",
                "start_date": today - datetime.timedelta(days=365 * 4),
                "is_public": True,
            },
        )
        for name, category, proficiency in [
            ("Python", "technical", 5),
            ("User-Centered Design", "research", 4),
            ("English", "language", 4),
        ]:
            Skill.objects.get_or_create(
                name=name,
                defaults={"category": category, "proficiency": proficiency, "is_public": True},
            )
        Achievement.objects.get_or_create(
            title="Best Paper Award",
            issuer="IEEE",
            defaults={
                "level": "international",
                "date": today - datetime.timedelta(days=200),
                "is_public": True,
            },
        )
        CommunityService.objects.get_or_create(
            title="Digital Literacy Workshop",
            defaults={
                "partner": "SMA Muhammadiyah 1",
                "date": today - datetime.timedelta(days=60),
                "is_public": True,
            },
        )
        OrganizationalRole.objects.get_or_create(
            organization="APSI PTMA",
            role="Regional Coordinator",
            defaults={"start_date": today - datetime.timedelta(days=365), "is_public": True},
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Seeded: 1 semester, 3 courses, 5 publications, 2 grants, 3 students, "
                "4 events, plus supporting CV/service records."
            )
        )
