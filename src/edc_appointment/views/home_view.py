from django.conf import settings
from django.views.generic.base import TemplateView
from edc_dashboard.view_mixins import EdcViewMixin


class HomeView(EdcViewMixin, TemplateView):

    template_name = f"edc_appointment/bootstrap{settings.EDC_BOOTSTRAP}/home.html"
