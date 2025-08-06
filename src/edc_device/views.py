from typing import Any

from django.apps import apps as django_apps
from django.views.generic.base import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin

from .view_mixins import EdcDeviceViewMixin


class HomeView(EdcViewMixin, NavbarViewMixin, EdcDeviceViewMixin, TemplateView):
    template_name = "edc_device/home.html"
    navbar_name = "edc_device"
    navbar_selected_item = "device"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        kwargs.update(
            {
                "project_name": (
                    f"{kwargs.get('project_name')}: "
                    f"{django_apps.get_app_config('edc_device').verbose_name}"
                )
            }
        )
        return super().get_context_data(**kwargs)

    def get_context_data_for_sites(self, **kwargs):
        return kwargs
