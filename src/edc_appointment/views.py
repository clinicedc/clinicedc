from edc_base.views.edc_base_view_mixin import EdcBaseViewMixin
from django.views.generic.base import TemplateView


class HomeView(EdcBaseViewMixin, TemplateView):

    template_name = 'edc_appointment/home.html'
