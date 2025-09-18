import datetime as dt
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import SubjectConsentV1Ext
from clinicedc_tests.sites import all_sites
from clinicedc_tests.visit_schedules.visit_schedule_appointment import (
    get_visit_schedule6,
)
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.test import TestCase, override_settings, tag
from django.utils import timezone

from edc_appointment.models import Appointment
from edc_appointment.utils import refresh_appointments
from edc_consent.consent_definition import ConsentDefinition
from edc_consent.consent_definition_extension import ConsentDefinitionExtension
from edc_consent.site_consents import site_consents
from edc_constants.constants import FEMALE, MALE, YES
from edc_facility.import_holidays import import_holidays
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites
from edc_visit_schedule.post_migrate_signals import populate_visit_schedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.utils import get_related_visit_model_cls

utc = ZoneInfo("UTC")
tz = ZoneInfo("Africa/Dar_es_Salaam")


@tag("appointment")
@override_settings(SITE_ID=10)
class TestNextAppointmentCrf(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()

    @time_machine.travel(dt.datetime(2025, 6, 11, 8, 00, tzinfo=utc))
    def setUp(self):
        self.user = User.objects.create_superuser("user_login", "u@example.com", "pass")

        consent_v1 = ConsentDefinition(
            "clinicedc_tests.subjectconsentv1",
            version="1",
            start=ResearchProtocolConfig().study_open_datetime,
            end=ResearchProtocolConfig().study_close_datetime,
            age_min=18,
            age_is_adult=18,
            age_max=64,
            gender=[MALE, FEMALE],
        )

        consent_v1_ext = ConsentDefinitionExtension(
            "clinicedc_tests.subjectconsentv1ext",
            version="1.1",
            start=consent_v1.start + relativedelta(months=2),
            extends=consent_v1,
            timepoints=[4],
        )
        site_consents.registry = {}
        site_consents.register(consent_v1, extended_by=consent_v1_ext)

        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        visit_schedule = get_visit_schedule6(consent_v1)
        site_visit_schedules.register(get_visit_schedule6(consent_v1))
        populate_visit_schedule()

        helper = Helper()
        self.subject_consent = helper.consent_and_put_on_schedule(
            visit_schedule_name=visit_schedule.name,
            schedule_name="schedule6",
            consent_definition=consent_v1,
        )
        self.subject_identifier = self.subject_consent.subject_identifier

    @override_settings(
        EDC_APPOINTMENT_ALLOW_SKIPPED_APPT_USING={
            "clinicedc_tests.nextappointmentcrf": ("appt_date", "visitschedule")
        }
    )
    @time_machine.travel(dt.datetime(2025, 6, 11, 8, 00, tzinfo=utc))
    def test_ok(self):
        self.assertEqual(4, Appointment.objects.all().count())
        subject_visit_model_cls = get_related_visit_model_cls()

        appointment = Appointment.objects.get(timepoint=0)
        subject_visit_model_cls.objects.create(
            report_datetime=appointment.appt_datetime,
            appointment=appointment,
            reason=SCHEDULED,
        )
        appointment = Appointment.objects.get(timepoint=1)
        subject_visit_model_cls.objects.create(
            report_datetime=appointment.appt_datetime,
            appointment=appointment,
            reason=SCHEDULED,
        )
        appointment = Appointment.objects.get(timepoint=2)
        subject_visit = subject_visit_model_cls(
            report_datetime=appointment.appt_datetime,
            appointment=appointment,
            reason=SCHEDULED,
        )
        subject_visit.save()

        traveller = time_machine.travel(appointment.appt_datetime + relativedelta(days=10))
        traveller.start()
        SubjectConsentV1Ext.objects.create(
            subject_consent=self.subject_consent,
            report_datetime=timezone.now(),
            site_id=self.subject_consent.site_id,
            agrees_to_extension=YES,
        )
        refresh_appointments(
            subject_identifier=self.subject_consent.subject_identifier,
            visit_schedule_name="visit_schedule6",
            schedule_name="schedule6",
        )

        self.assertEqual(5, Appointment.objects.all().count())
        traveller.stop()

        appointment = Appointment.objects.get(timepoint=3)
        traveller = time_machine.travel(appointment.appt_datetime)
        traveller.start()
        subject_visit = subject_visit_model_cls.objects.create(
            report_datetime=timezone.now(),
            appointment=appointment,
            reason=SCHEDULED,
        )
        self.assertEqual(subject_visit.consent_version, "1.1")
