from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages import SUCCESS
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View
from edc_dashboard import url_names
from edc_visit_schedule.site_visit_schedules import site_visit_schedules


class RefreshAppointmentsView(LoginRequiredMixin, View):
    onschedule_model = None

    @staticmethod
    def refresh_appointments(
        subject_identifier: str = None,
        visit_schedule: str = None,
        schedule: str = None,
        **kwargs,
    ):  # noqa
        visit_schedule = site_visit_schedules.get_visit_schedule(visit_schedule)
        schedule = visit_schedule.schedules.get(schedule)
        schedule.refresh_schedule(subject_identifier=subject_identifier)
        return subject_identifier

    def get(self, request, *args, **kwargs):
        subject_identifier = self.refresh_appointments(**kwargs)
        url_name = url_names.get("subject_dashboard_url")
        args = (subject_identifier,)
        url = reverse(url_name, args=args)
        messages.add_message(
            request, SUCCESS, f"The appointments for {subject_identifier} have been refreshed "
        )
        return HttpResponseRedirect(url)
