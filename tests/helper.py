from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.conf import settings
from faker import Faker

from edc_appointment.creators import UnscheduledAppointmentCreator
from edc_consent.consent_definition import ConsentDefinition
from edc_constants.constants import FEMALE
from edc_registration.models import RegisteredSubject
from edc_sites import site_sites
from edc_utils import get_utcnow
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

if TYPE_CHECKING:
    from edc_appointment.models import Appointment

fake = Faker()


class Helper:
    def __init__(self, subject_identifier=None, now=None):
        self.subject_identifier = subject_identifier
        self.now = now or get_utcnow()

    @property
    def screening_model_cls(self):
        """Returns a screening model class.

        Defaults to tests.subjectscreening
        """
        try:
            return django_apps.get_model(settings.SUBJECT_SCREENING_MODEL)
        except LookupError:
            return django_apps.get_model("tests.subjectscreening")

    def consent_and_put_on_schedule(
        self,
        visit_schedule_name: str = None,
        schedule_name: str = None,
        age_in_years: int | None = None,
        report_datetime: datetime | None = None,
        onschedule_datetime: datetime | None = None,
        consent_definition: ConsentDefinition | None = None,
    ):
        report_datetime = report_datetime or self.now
        RegisteredSubject.objects.filter(
            subject_identifier=self.subject_identifier
        ).delete()

        first_name = fake.first_name
        last_name = fake.last_name
        initials = f"{first_name[0]}{last_name[0]}".upper()

        subject_screening = self.screening_model_cls.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=report_datetime or self.now,
            screening_identifier=uuid4(),
            age_in_years=age_in_years or 25,
            first_name=first_name,
            last_name=last_name,
            initials=initials,
            guardian_name=None,
        )
        schedule: Schedule = site_visit_schedules.get_visit_schedule(
            visit_schedule_name
        ).schedules.get(schedule_name)

        cdef = consent_definition or schedule.get_consent_definition(
            report_datetime=report_datetime,
            site=site_sites.get(subject_screening.site.id),
        )
        identity = str(uuid4())
        subject_consent = cdef.model_cls.objects.create(
            screening_identifier=subject_screening.screening_identifier,
            subject_identifier=self.subject_identifier,
            consent_datetime=report_datetime or self.now,
            dob=self.now - relativedelta(years=age_in_years or 25),
            identity=identity,
            confirm_identity=identity,
            gender=FEMALE,
        )

        visit_schedule = site_visit_schedules.get_visit_schedule(visit_schedule_name)
        schedule = visit_schedule.schedules.get(schedule_name)
        schedule.put_on_schedule(
            self.subject_identifier,
            onschedule_datetime or subject_consent.consent_datetime,
        )
        return subject_consent

    @staticmethod
    def add_unscheduled_appointment(appointment: Appointment | None = None):
        creator = UnscheduledAppointmentCreator(
            subject_identifier=appointment.subject_identifier,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            suggested_visit_code_sequence=appointment.visit_code_sequence + 1,
            facility=appointment.facility,
        )
        return creator.appointment
