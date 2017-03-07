from edc_base.view_mixins import EdcBaseViewMixin
from django.views.generic.base import TemplateView


class HomeView(EdcBaseViewMixin, TemplateView):

    template_name = 'edc_appointment/home.html'
