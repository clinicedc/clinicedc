from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin


class HomeView(EdcViewMixin, NavbarViewMixin, TemplateView):

    template_name = f"edc_dashboard/bootstrap{settings.EDC_BOOTSTRAP}/home.html"
    navbar_name = "edc_base"
    navbar_selected_item = "edc_base"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            edc_packages=["not available"],
            third_party_packages=["not available"],
            installed_apps=settings.INSTALLED_APPS,
        )
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
