from django.conf import settings
from django.views.generic import TemplateView
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin


class BrowserPrintLabelsView(EdcViewMixin, NavbarViewMixin, TemplateView):
    template_name = "edc_label/browser_print_labels.html"
    navbar_name = "edc_label"
    navbar_selected_item = "label"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        browser_print_page_auto_back = getattr(
            settings, "EDC_LABEL_BROWSER_PRINT_PAGE_AUTO_BACK", True
        )
        context.update(browser_print_page_auto_back=browser_print_page_auto_back)
        return context
