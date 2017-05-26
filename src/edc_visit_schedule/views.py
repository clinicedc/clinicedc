from django.views.generic.base import TemplateView

from edc_base.view_mixins import EdcBaseViewMixin

from .site_visit_schedules import site_visit_schedules
from .visit_schedule import VisitScheduleError


class HomeView(EdcBaseViewMixin, TemplateView):

    template_name = 'edc_visit_schedule/home.html'

    def get_context_data(self, **kwargs):
        context_data = super(HomeView, self).get_context_data(**kwargs)
        try:
            selected_visit_schedule = site_visit_schedules.get_visit_schedule(
                visit_schedule_name=self.kwargs.get('visit_schedule'))
        except VisitScheduleError:
            selected_visit_schedule = None
        context_data.update({
            'visit_schedules': site_visit_schedules.registry,
            'selected_visit_schedule': selected_visit_schedule})
        return context_data
