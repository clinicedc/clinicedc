from django.views.generic.base import TemplateView

from edc_base.views import EdcBaseViewMixin
from edc_consent.admin import edc_consent_admin
from edc_consent.site_consent_types import site_consent_types


class HomeView(EdcBaseViewMixin, TemplateView):

    template_name = 'edc_consent/home.html'

    def __init__(self, *args, **kwargs):
        super(HomeView, self).__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            edc_consent_admin=edc_consent_admin,
            consent_types=site_consent_types.all(),
        )
        return context
