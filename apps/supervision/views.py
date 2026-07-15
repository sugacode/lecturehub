from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.common.htmx import htmx_row_deleted

from .forms import MilestoneForm, StudentForm, SupervisionLogForm
from .models import Milestone, Student, SupervisionLog


class ToastFormMixin:
    success_message = "Saved."

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response


class HtmxDeleteView(LoginRequiredMixin, DeleteView):
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        label = str(self.object)
        self.object.delete()
        if request.headers.get("HX-Request"):
            return htmx_row_deleted(f'Deleted "{label}".')
        messages.success(request, f'Deleted "{label}".')
        response = HttpResponse(status=302)
        response["Location"] = self.get_success_url()
        return response


class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = "supervision/student_list.html"
    context_object_name = "students"


class StudentCreateView(LoginRequiredMixin, ToastFormMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = "supervision/student_form.html"
    success_url = reverse_lazy("supervision:student_list")
    success_message = "Student added."


class StudentUpdateView(LoginRequiredMixin, ToastFormMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = "supervision/student_form.html"
    success_url = reverse_lazy("supervision:student_list")
    success_message = "Student updated."


class StudentDeleteView(HtmxDeleteView):
    model = Student
    success_url = reverse_lazy("supervision:student_list")


@login_required
def student_timeline(request: HttpRequest, pk: int) -> HttpResponse:
    """Per-student timeline merging milestones and supervision logs by date."""
    student = get_object_or_404(Student, pk=pk)
    timeline = []
    for milestone in student.milestones.all():
        timeline.append(
            {
                "date": milestone.completed_date or milestone.due_date,
                "kind": "milestone",
                "object": milestone,
            }
        )
    for log in student.logs.all():
        timeline.append({"date": log.date, "kind": "log", "object": log})
    timeline.sort(key=lambda entry: entry["date"], reverse=True)

    context = {
        "student": student,
        "timeline": timeline,
        "milestone_form": MilestoneForm(),
        "log_form": SupervisionLogForm(),
    }
    return render(request, "supervision/student_timeline.html", context)


@login_required
def milestone_create(request: HttpRequest, student_pk: int) -> HttpResponse:
    student = get_object_or_404(Student, pk=student_pk)
    if request.method == "POST":
        form = MilestoneForm(request.POST)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.student = student
            milestone.save()
            messages.success(request, "Milestone added.")
    return redirect("supervision:student_timeline", pk=student.pk)


@login_required
def log_create(request: HttpRequest, student_pk: int) -> HttpResponse:
    student = get_object_or_404(Student, pk=student_pk)
    if request.method == "POST":
        form = SupervisionLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.student = student
            log.save()
            messages.success(request, "Supervision log added.")
    return redirect("supervision:student_timeline", pk=student.pk)


class MilestoneDeleteView(HtmxDeleteView):
    model = Milestone

    def get_success_url(self) -> str:
        return reverse("supervision:student_timeline", args=[self.object.student_id])


class SupervisionLogDeleteView(HtmxDeleteView):
    model = SupervisionLog

    def get_success_url(self) -> str:
        return reverse("supervision:student_timeline", args=[self.object.student_id])
