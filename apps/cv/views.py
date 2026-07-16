from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.accounts.models import Profile
from apps.common.htmx import htmx_row_deleted

from .forms import (
    AchievementForm,
    EducationForm,
    PositionForm,
    SkillForm,
    TrainingCertificationForm,
)
from .models import Achievement, Education, Position, Skill, TrainingCertification
from .pdf_academic import build_academic_cv_pdf
from .pdf_data import get_cv_context
from .pdf_europass import build_europass_cv_pdf


class ToastFormMixin:
    """Adds a success-toast Django message on create/update, shared by all CV CRUD views."""

    success_message = "Saved."

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response


class HtmxDeleteView(LoginRequiredMixin, DeleteView):
    """Delete view that responds to hx-post row-delete requests with a toast + empty row swap."""

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        label = str(self.object)
        self.object.delete()
        if request.headers.get("HX-Request"):
            return htmx_row_deleted(f'Deleted "{label}".')
        messages.success(request, f'Deleted "{label}".')
        response = HttpResponse(status=302)
        response["Location"] = str(self.success_url)
        return response


# Education


class EducationListView(LoginRequiredMixin, ListView):
    model = Education
    template_name = "cv/education_list.html"
    context_object_name = "educations"


class EducationCreateView(LoginRequiredMixin, ToastFormMixin, CreateView):
    model = Education
    form_class = EducationForm
    template_name = "cv/education_form.html"
    success_url = reverse_lazy("cv:education_list")
    success_message = "Education added."


class EducationUpdateView(LoginRequiredMixin, ToastFormMixin, UpdateView):
    model = Education
    form_class = EducationForm
    template_name = "cv/education_form.html"
    success_url = reverse_lazy("cv:education_list")
    success_message = "Education updated."


class EducationDeleteView(HtmxDeleteView):
    model = Education
    success_url = reverse_lazy("cv:education_list")


# Position


class PositionListView(LoginRequiredMixin, ListView):
    model = Position
    template_name = "cv/position_list.html"
    context_object_name = "positions"


class PositionCreateView(LoginRequiredMixin, ToastFormMixin, CreateView):
    model = Position
    form_class = PositionForm
    template_name = "cv/position_form.html"
    success_url = reverse_lazy("cv:position_list")
    success_message = "Position added."


class PositionUpdateView(LoginRequiredMixin, ToastFormMixin, UpdateView):
    model = Position
    form_class = PositionForm
    template_name = "cv/position_form.html"
    success_url = reverse_lazy("cv:position_list")
    success_message = "Position updated."


class PositionDeleteView(HtmxDeleteView):
    model = Position
    success_url = reverse_lazy("cv:position_list")


# Achievement


class AchievementListView(LoginRequiredMixin, ListView):
    model = Achievement
    template_name = "cv/achievement_list.html"
    context_object_name = "achievements"


class AchievementCreateView(LoginRequiredMixin, ToastFormMixin, CreateView):
    model = Achievement
    form_class = AchievementForm
    template_name = "cv/achievement_form.html"
    success_url = reverse_lazy("cv:achievement_list")
    success_message = "Achievement added."


class AchievementUpdateView(LoginRequiredMixin, ToastFormMixin, UpdateView):
    model = Achievement
    form_class = AchievementForm
    template_name = "cv/achievement_form.html"
    success_url = reverse_lazy("cv:achievement_list")
    success_message = "Achievement updated."


class AchievementDeleteView(HtmxDeleteView):
    model = Achievement
    success_url = reverse_lazy("cv:achievement_list")


# Skill


class SkillListView(LoginRequiredMixin, ListView):
    model = Skill
    template_name = "cv/skill_list.html"
    context_object_name = "skills"


class SkillCreateView(LoginRequiredMixin, ToastFormMixin, CreateView):
    model = Skill
    form_class = SkillForm
    template_name = "cv/skill_form.html"
    success_url = reverse_lazy("cv:skill_list")
    success_message = "Skill added."


class SkillUpdateView(LoginRequiredMixin, ToastFormMixin, UpdateView):
    model = Skill
    form_class = SkillForm
    template_name = "cv/skill_form.html"
    success_url = reverse_lazy("cv:skill_list")
    success_message = "Skill updated."


class SkillDeleteView(HtmxDeleteView):
    model = Skill
    success_url = reverse_lazy("cv:skill_list")


# TrainingCertification


class TrainingCertificationListView(LoginRequiredMixin, ListView):
    model = TrainingCertification
    template_name = "cv/training_list.html"
    context_object_name = "trainings"


class TrainingCertificationCreateView(LoginRequiredMixin, ToastFormMixin, CreateView):
    model = TrainingCertification
    form_class = TrainingCertificationForm
    template_name = "cv/training_form.html"
    success_url = reverse_lazy("cv:training_list")
    success_message = "Training added."


class TrainingCertificationUpdateView(LoginRequiredMixin, ToastFormMixin, UpdateView):
    model = TrainingCertification
    form_class = TrainingCertificationForm
    template_name = "cv/training_form.html"
    success_url = reverse_lazy("cv:training_list")
    success_message = "Training updated."


class TrainingCertificationDeleteView(HtmxDeleteView):
    model = TrainingCertification
    success_url = reverse_lazy("cv:training_list")


def cv_export(request: HttpRequest) -> HttpResponse:
    """Generate a CV PDF. ?style=academic (default) or ?style=europass.

    Public (unauthenticated) requests only ever see is_public=True records; in
    PUBLIC_PAGES_MODE=unlisted they must also supply ?slug=<profile.public_slug>.
    """
    if not request.user.is_authenticated:
        profile = Profile.objects.first()
        if settings.PUBLIC_PAGES_MODE == "unlisted":
            slug = request.GET.get("slug")
            if not profile or not slug or slug != profile.public_slug:
                raise Http404
        public_only = True
    else:
        public_only = False

    style = request.GET.get("style", "academic")
    context = get_cv_context(public_only=public_only)
    if style == "europass":
        pdf_bytes = build_europass_cv_pdf(context)
    else:
        pdf_bytes = build_academic_cv_pdf(context)
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="cv-{style}.pdf"'
    return response
