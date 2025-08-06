from typing import Any

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView

from edc_navbar import NavbarViewMixin

from ..view_mixins import EdcViewMixin


class HomeView(EdcViewMixin, NavbarViewMixin, TemplateView):
    template_name = "edc_dashboard/home.html"
    navbar_name = "edc_dashboard"
    navbar_selected_item = "edc_dashboard"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        kwargs.update(
            edc_packages=["not available"],
            third_party_packages=["not available"],
            installed_apps=settings.INSTALLED_APPS,
        )
        return super().get_context_data(**kwargs)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
