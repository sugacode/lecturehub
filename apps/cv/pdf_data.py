from apps.accounts.models import Profile
from apps.publications.models import IntellectualProperty, Publication
from apps.research.models import Grant
from apps.service.models import CommunityService, OrganizationalRole
from apps.supervision.models import Student

from .models import Achievement, Education, Position, Skill, TrainingCertification


def get_cv_context(*, public_only: bool = False) -> dict:
    """Gather every record needed to render a CV, for either PDF style or the public page.

    Set public_only=True to include only records flagged is_public (used by the
    public CV page and its PDF export in Phase 9).
    """

    def maybe_public(qs):
        return qs.filter(is_public=True) if public_only else qs

    publications = list(maybe_public(Publication.objects.all()))
    pub_type_labels = dict(Publication.PubType.choices)
    pub_type_order = [choice[0] for choice in Publication.PubType.choices]
    publications_by_type = []
    for pub_type in pub_type_order:
        group = [p for p in publications if p.pub_type == pub_type]
        group.sort(key=lambda p: (-p.year, p.title))
        if group:
            publications_by_type.append((pub_type_labels[pub_type], group))

    by_indexing: dict[str, int] = {}
    for pub in publications:
        by_indexing[pub.indexing] = by_indexing.get(pub.indexing, 0) + 1

    students = Student.objects.all()

    return {
        "profile": Profile.objects.first(),
        "educations": maybe_public(Education.objects.all()),
        "positions": maybe_public(Position.objects.all()),
        "achievements": maybe_public(Achievement.objects.all()),
        "skills": maybe_public(Skill.objects.all()),
        "trainings": maybe_public(TrainingCertification.objects.all()),
        "publications_by_type": publications_by_type,
        "publication_stats": {"total": len(publications), "by_indexing": by_indexing},
        "intellectual_properties": maybe_public(IntellectualProperty.objects.all()),
        "grants": maybe_public(Grant.objects.all()),
        "community_services": maybe_public(CommunityService.objects.all()),
        "organizational_roles": maybe_public(OrganizationalRole.objects.all()),
        "student_count": students.count(),
        "active_student_count": sum(1 for s in students if s.is_active),
    }
