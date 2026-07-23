from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.common.htmx import htmx_row_deleted

from .forms import DocumentForm, SharedLinkForm
from .models import Document, SharedLink


class DocumentListView(LoginRequiredMixin, ListView):
    """List documents with category filter and search across title/tags."""

    model = Document
    template_name = "documents/document_list.html"
    context_object_name = "documents"
    paginate_by = 25

    def get_queryset(self):
        qs = Document.objects.all()
        category = self.request.GET.get("category")
        query = self.request.GET.get("q")
        if category:
            qs = qs.filter(category=category)
        if query:
            qs = qs.filter(Q(title__icontains=query) | Q(tags__icontains=query))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Document.Category.choices
        context["selected_category"] = self.request.GET.get("category", "")
        context["query"] = self.request.GET.get("q", "")
        return context


class DocumentCreateView(LoginRequiredMixin, CreateView):
    model = Document
    form_class = DocumentForm
    template_name = "documents/document_form.html"
    success_url = reverse_lazy("documents:document_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Document uploaded.")
        return response


class DocumentUpdateView(LoginRequiredMixin, UpdateView):
    model = Document
    form_class = DocumentForm
    template_name = "documents/document_form.html"
    success_url = reverse_lazy("documents:document_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Document updated.")
        return response


class DocumentDeleteView(LoginRequiredMixin, DeleteView):
    model = Document
    success_url = reverse_lazy("documents:document_list")

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        title = self.object.title
        self.object.delete()
        if request.headers.get("HX-Request"):
            return htmx_row_deleted(f'Deleted "{title}".')
        messages.success(request, f'Deleted "{title}".')
        response = HttpResponse(status=302)
        response["Location"] = str(self.success_url)
        return response


class SharedLinkListView(LoginRequiredMixin, ListView):
    model = SharedLink
    template_name = "documents/shared_link_list.html"
    context_object_name = "shared_links"


class SharedLinkCreateView(LoginRequiredMixin, CreateView):
    model = SharedLink
    form_class = SharedLinkForm
    template_name = "documents/shared_link_form.html"
    success_url = reverse_lazy("documents:shared_link_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Shared link created.")
        return response


class SharedLinkUpdateView(LoginRequiredMixin, UpdateView):
    model = SharedLink
    form_class = SharedLinkForm
    template_name = "documents/shared_link_form.html"
    success_url = reverse_lazy("documents:shared_link_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Shared link updated.")
        return response


class SharedLinkDeleteView(LoginRequiredMixin, DeleteView):
    model = SharedLink
    success_url = reverse_lazy("documents:shared_link_list")

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        name = self.object.name
        self.object.delete()
        if request.headers.get("HX-Request"):
            return htmx_row_deleted(f'Deleted "{name}".')
        messages.success(request, f'Deleted "{name}".')
        response = HttpResponse(status=302)
        response["Location"] = str(self.success_url)
        return response


def shared_link_redirect(request: HttpRequest, slug: str) -> HttpResponse:
    """Public, unauthenticated redirect: /s/<slug>/ -> the link's original_url."""
    link = get_object_or_404(SharedLink, slug=slug)
    return HttpResponseRedirect(link.original_url)
