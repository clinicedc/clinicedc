from django.apps import apps as django_apps
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin

from .view_mixins import EdcDeviceViewMixin


class HomeView(EdcViewMixin, NavbarViewMixin, EdcDeviceViewMixin, TemplateView):

    template_name = f"edc_device/bootstrap{settings.EDC_BOOTSTRAP}/home.html"
    navbar_name = "edc_device"
    navbar_selected_item = "device"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app_config = django_apps.get_app_config("edc_device")
        project_name = context.get("project_name")
        context.update({"project_name": f"{project_name}: {app_config.verbose_name}"})
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
