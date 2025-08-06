from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View

from edc_appointment.utils import refresh_appointments
from edc_dashboard.url_names import url_names


class RefreshAppointmentsView(LoginRequiredMixin, View):
    onschedule_model = None

    def refresh_appointments(
        self,
        subject_identifier: str = None,
        visit_schedule_name: str = None,
        schedule_name: str = None,
        **kwargs,
    ) -> tuple[str, str]:
        return refresh_appointments(
            subject_identifier=subject_identifier,
            visit_schedule_name=visit_schedule_name,
            schedule_name=schedule_name,
            request=self.request,
        )

    def get(self, request, *args, **kwargs):
        subject_identifier, status = self.refresh_appointments(**kwargs)
        url_name = url_names.get("subject_dashboard_url")
        args = (subject_identifier,)
        url = reverse(url_name, args=args)
        return HttpResponseRedirect(url)
