from django.conf import settings
from django.views.generic.base import TemplateView
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin

from ..admin_site import edc_consent_admin
from ..site_consents import site_consents


class HomeView(EdcViewMixin, NavbarViewMixin, TemplateView):

    template_name = f"edc_consent/bootstrap{settings.EDC_BOOTSTRAP}/home.html"
    navbar_name = "edc_consent"
    navbar_selected_item = "consent"

    def __init__(self, *args, **kwargs):
        super(HomeView, self).__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(edc_consent_admin=edc_consent_admin, consents=site_consents.consents)
        return context
