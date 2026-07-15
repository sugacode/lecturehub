from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.common.htmx import htmx_row_deleted

from .forms import DeliverableForm, GrantForm
from .models import Deliverable, Grant


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


class GrantListView(LoginRequiredMixin, ListView):
    model = Grant
    template_name = "research/grant_list.html"
    context_object_name = "grants"


class GrantCreateView(LoginRequiredMixin, ToastFormMixin, CreateView):
    model = Grant
    form_class = GrantForm
    template_name = "research/grant_form.html"
    success_url = reverse_lazy("research:grant_list")
    success_message = "Grant added."


class GrantUpdateView(LoginRequiredMixin, ToastFormMixin, UpdateView):
    model = Grant
    form_class = GrantForm
    template_name = "research/grant_form.html"
    success_url = reverse_lazy("research:grant_list")
    success_message = "Grant updated."


class GrantDeleteView(HtmxDeleteView):
    model = Grant
    success_url = reverse_lazy("research:grant_list")


@login_required
def grant_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Grant detail page with its deliverables and an inline add-deliverable form."""
    grant = get_object_or_404(Grant, pk=pk)
    return render(
        request,
        "research/grant_detail.html",
        {"grant": grant, "deliverable_form": DeliverableForm()},
    )


@login_required
def deliverable_create(request: HttpRequest, grant_pk: int) -> HttpResponse:
    grant = get_object_or_404(Grant, pk=grant_pk)
    if request.method == "POST":
        form = DeliverableForm(request.POST)
        if form.is_valid():
            deliverable = form.save(commit=False)
            deliverable.grant = grant
            deliverable.save()
            messages.success(request, "Deliverable added.")
    return redirect("research:grant_detail", pk=grant.pk)


class DeliverableUpdateView(LoginRequiredMixin, ToastFormMixin, UpdateView):
    model = Deliverable
    form_class = DeliverableForm
    template_name = "research/deliverable_form.html"
    success_message = "Deliverable updated."

    def get_success_url(self) -> str:
        return reverse("research:grant_detail", args=[self.object.grant_id])


class DeliverableDeleteView(HtmxDeleteView):
    model = Deliverable

    def get_success_url(self) -> str:
        return reverse("research:grant_detail", args=[self.object.grant_id])
