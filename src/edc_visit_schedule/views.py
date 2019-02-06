from django.conf import settings
from django.views.generic.base import TemplateView

from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar.view_mixin import NavbarViewMixin

from .site_visit_schedules import site_visit_schedules, SiteVisitScheduleError


class HomeView(EdcBaseViewMixin, NavbarViewMixin, TemplateView):

    template_name = f"edc_visit_schedule/bootstrap{settings.EDC_BOOTSTRAP}/home.html"
    navbar_name = "edc_visit_schedule"
    navbar_selected_item = "visit_schedule"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        try:
            selected_visit_schedule = site_visit_schedules.get_visit_schedule(
                visit_schedule_name=self.kwargs.get("visit_schedule")
            )
        except SiteVisitScheduleError:
            selected_visit_schedule = None
        context_data.update(
            {
                "visit_schedules": site_visit_schedules.registry,
                "selected_visit_schedule": selected_visit_schedule,
            }
        )
        return context_data
