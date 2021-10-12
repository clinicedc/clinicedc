from django.views.generic import TemplateView
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin


class BrowserPrintLabelsView(EdcViewMixin, NavbarViewMixin, TemplateView):

    template_name = f"edc_label/browser_print_labels.html"
    navbar_name = "edc_dashboard"
    navbar_selected_item = "edc_dashboard"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
