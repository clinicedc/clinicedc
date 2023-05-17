from django.apps import apps as django_apps
from django.views.generic.base import TemplateView
from edc_dashboard.utils import get_bootstrap_version
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin

from ..constants import CLINIC_LABEL_PRINTER, LAB_LABEL_PRINTER, PRINT_SERVER_NAME
from ..view_mixins import EdcLabelViewMixin


class PrinterSetupView(EdcViewMixin, NavbarViewMixin, EdcLabelViewMixin, TemplateView):
    template_name = f"edc_label/bootstrap{get_bootstrap_version()}/printer_setup.html"
    navbar_name = "edc_label"
    navbar_selected_item = "label"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            CLINIC_LABEL_PRINTER=CLINIC_LABEL_PRINTER,
            LAB_LABEL_PRINTER=LAB_LABEL_PRINTER,
            PRINT_SERVER_NAME=PRINT_SERVER_NAME,
            label_templates=list(
                django_apps.get_app_config("edc_label").label_templates.keys()
            ),
        )
        return context
