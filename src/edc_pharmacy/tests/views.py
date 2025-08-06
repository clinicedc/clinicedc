from typing import Any

from django.conf import settings
from django.views.generic import TemplateView
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_randomization.site_randomizers import site_randomizers


class HomeView(EdcViewMixin, NavbarViewMixin, TemplateView):
    template_name = "edc_pharmacy/home.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "home"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        randomizer_cls = site_randomizers.get("default")
        edc_randomization_url_name = (
            "edc_randomization_admin:"
            f"{randomizer_cls.model_cls()._meta.label_lower.replace('.', '_')}_changelist"
        )
        kwargs.update(edc_randomization_url_name=edc_randomization_url_name)
        return super().get_context_data(**kwargs)
