"""Invalidates the public CV cache (used by /p/cv/, /p/schedule/, and the
front-page landing resume) whenever any record feeding get_cv_context()
changes — otherwise an edit (e.g. uploading a profile photo) doesn't show up
on those pages for up to 5 minutes, the cache's TTL.
"""

from django.core.cache import cache
from django.db.models.signals import post_delete, post_save

from apps.accounts.models import Profile
from apps.cv.models import Achievement, Education, Position, Skill, TrainingCertification
from apps.publications.models import IntellectualProperty, Publication
from apps.research.models import Grant
from apps.service.models import CommunityService, OrganizationalRole
from apps.supervision.models import Student

CV_CONTEXT_MODELS = [
    Profile,
    Education,
    Position,
    Achievement,
    Skill,
    TrainingCertification,
    Publication,
    IntellectualProperty,
    Grant,
    CommunityService,
    OrganizationalRole,
    Student,
]


def _invalidate_public_cv_cache(**kwargs):
    cache.delete("public_cv_context")


def connect():
    for model in CV_CONTEXT_MODELS:
        uid = f"invalidate_public_cv_cache_{model.__name__}"
        post_save.connect(_invalidate_public_cv_cache, sender=model, dispatch_uid=f"{uid}_save")
        post_delete.connect(_invalidate_public_cv_cache, sender=model, dispatch_uid=f"{uid}_delete")
