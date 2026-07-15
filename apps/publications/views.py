from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.common.htmx import htmx_row_deleted

from .crossref import CrossRefLookupError, fetch_doi_metadata
from .forms import DoiImportForm, IntellectualPropertyForm, PublicationForm
from .models import IntellectualProperty, Publication


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
        response["Location"] = str(self.success_url)
        return response


class PublicationListView(LoginRequiredMixin, ListView):
    model = Publication
    template_name = "publications/publication_list.html"
    context_object_name = "publications"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stats"] = Publication.objects.stats()
        return context


class PublicationCreateView(LoginRequiredMixin, ToastFormMixin, CreateView):
    model = Publication
    form_class = PublicationForm
    template_name = "publications/publication_form.html"
    success_url = reverse_lazy("publications:publication_list")
    success_message = "Publication added."

    def get_initial(self):
        initial = super().get_initial()
        prefill = self.request.session.pop("doi_prefill", None)
        if prefill:
            initial.update(prefill)
        return initial


class PublicationUpdateView(LoginRequiredMixin, ToastFormMixin, UpdateView):
    model = Publication
    form_class = PublicationForm
    template_name = "publications/publication_form.html"
    success_url = reverse_lazy("publications:publication_list")
    success_message = "Publication updated."


class PublicationDeleteView(HtmxDeleteView):
    model = Publication
    success_url = reverse_lazy("publications:publication_list")


@login_required
def import_by_doi(request: HttpRequest) -> HttpResponse:
    """Accept a DOI, fetch metadata from CrossRef, and prefill the Publication create form."""
    if request.method == "POST":
        form = DoiImportForm(request.POST)
        if form.is_valid():
            try:
                metadata = fetch_doi_metadata(form.cleaned_data["doi"])
            except CrossRefLookupError as exc:
                messages.error(request, str(exc))
            else:
                request.session["doi_prefill"] = metadata
                messages.success(request, "Metadata fetched. Review and save below.")
                return redirect("publications:publication_create")
    else:
        form = DoiImportForm()
    return render(request, "publications/doi_import.html", {"form": form})


class IntellectualPropertyListView(LoginRequiredMixin, ListView):
    model = IntellectualProperty
    template_name = "publications/ip_list.html"
    context_object_name = "ips"


class IntellectualPropertyCreateView(LoginRequiredMixin, ToastFormMixin, CreateView):
    model = IntellectualProperty
    form_class = IntellectualPropertyForm
    template_name = "publications/ip_form.html"
    success_url = reverse_lazy("publications:ip_list")
    success_message = "Intellectual property added."


class IntellectualPropertyUpdateView(LoginRequiredMixin, ToastFormMixin, UpdateView):
    model = IntellectualProperty
    form_class = IntellectualPropertyForm
    template_name = "publications/ip_form.html"
    success_url = reverse_lazy("publications:ip_list")
    success_message = "Intellectual property updated."


class IntellectualPropertyDeleteView(HtmxDeleteView):
    model = IntellectualProperty
    success_url = reverse_lazy("publications:ip_list")
