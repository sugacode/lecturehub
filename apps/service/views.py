from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.common.htmx import htmx_row_deleted

from .forms import CommunityServiceForm, OrganizationalRoleForm
from .models import CommunityService, OrganizationalRole


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


# CommunityService


class CommunityServiceListView(LoginRequiredMixin, ListView):
    model = CommunityService
    template_name = "service/community_service_list.html"
    context_object_name = "services"


class CommunityServiceCreateView(LoginRequiredMixin, ToastFormMixin, CreateView):
    model = CommunityService
    form_class = CommunityServiceForm
    template_name = "service/community_service_form.html"
    success_url = reverse_lazy("service:community_service_list")
    success_message = "Community service added."


class CommunityServiceUpdateView(LoginRequiredMixin, ToastFormMixin, UpdateView):
    model = CommunityService
    form_class = CommunityServiceForm
    template_name = "service/community_service_form.html"
    success_url = reverse_lazy("service:community_service_list")
    success_message = "Community service updated."


class CommunityServiceDeleteView(HtmxDeleteView):
    model = CommunityService
    success_url = reverse_lazy("service:community_service_list")


# OrganizationalRole


class OrganizationalRoleListView(LoginRequiredMixin, ListView):
    model = OrganizationalRole
    template_name = "service/organizational_role_list.html"
    context_object_name = "roles"


class OrganizationalRoleCreateView(LoginRequiredMixin, ToastFormMixin, CreateView):
    model = OrganizationalRole
    form_class = OrganizationalRoleForm
    template_name = "service/organizational_role_form.html"
    success_url = reverse_lazy("service:organizational_role_list")
    success_message = "Organizational role added."


class OrganizationalRoleUpdateView(LoginRequiredMixin, ToastFormMixin, UpdateView):
    model = OrganizationalRole
    form_class = OrganizationalRoleForm
    template_name = "service/organizational_role_form.html"
    success_url = reverse_lazy("service:organizational_role_list")
    success_message = "Organizational role updated."


class OrganizationalRoleDeleteView(HtmxDeleteView):
    model = OrganizationalRole
    success_url = reverse_lazy("service:organizational_role_list")
