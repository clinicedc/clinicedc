from django.conf import settings
from django.views.generic.base import TemplateView
from edc_base.view_mixins import EdcBaseViewMixin


class HomeView(EdcBaseViewMixin, TemplateView):

    template_name = f'edc_appointment/bootstrap{settings.EDC_BOOTSTRAP}/home.html'
