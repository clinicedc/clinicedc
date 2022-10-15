from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.conf import settings
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from edc_appointment.creators import UnscheduledAppointmentCreator

if TYPE_CHECKING:
    from edc_appointment.models import Appointment


class Helper:
    def __init__(self, subject_identifier=None, now=None):
        self.subject_identifier = subject_identifier
        self.now = now or get_utcnow()

    @property
    def screening_model_cls(self):
        """Returns a screening model class.

        Defaults to edc_appointment.subjectscreening
        """
        try:
            return django_apps.get_model(settings.SUBJECT_SCREENING_MODEL)
        except LookupError:
            return django_apps.get_model("edc_appointment_app.subjectscreening")

    @property
    def consent_model_cls(self):
        """Returns a consent model class.

        Defaults to edc_appointment.subjectconsent
        """
        try:
            return django_apps.get_model(settings.SUBJECT_CONSENT_MODEL)
        except LookupError:
            return django_apps.get_model("edc_appointment_app.subjectconsent")

    def consent_and_put_on_schedule(
        self,
        subject_identifier=None,
        visit_schedule_name=None,
        schedule_name=None,
        age_in_years=None,
    ):
        subject_identifier = subject_identifier or self.subject_identifier
        self.screening_model_cls.objects.create(
            subject_identifier=subject_identifier,
            report_datetime=self.now,
            screening_identifier=uuid4(),
            age_in_years=age_in_years or 25,
        )
        subject_consent = self.consent_model_cls.objects.create(
            subject_identifier=subject_identifier,
            consent_datetime=self.now,
            dob=self.now - relativedelta(years=age_in_years or 25),
        )
        visit_schedule = site_visit_schedules.get_visit_schedule(
            visit_schedule_name or "visit_schedule1"
        )
        schedule = visit_schedule.schedules.get(schedule_name or "schedule1")
        schedule.put_on_schedule(
            subject_identifier=subject_consent.subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime,
        )
        return subject_consent

    @staticmethod
    def add_unscheduled_appointment(appointment: Appointment | None = None):
        creator = UnscheduledAppointmentCreator(
            subject_identifier=appointment.subject_identifier,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            visit_code_sequence=appointment.visit_code_sequence + 1,
            facility=appointment.facility,
            timepoint=appointment.timepoint,
        )
        return creator.appointment
