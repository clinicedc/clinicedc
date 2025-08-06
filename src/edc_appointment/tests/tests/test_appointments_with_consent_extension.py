import datetime as dt
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from edc_consent.consent_definition import ConsentDefinition
from edc_consent.consent_definition_extension import ConsentDefinitionExtension
from edc_consent.site_consents import site_consents
from edc_constants.constants import FEMALE, MALE, YES
from edc_facility import import_holidays
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_utils import get_utcnow
from edc_visit_schedule.post_migrate_signals import populate_visit_schedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.utils import get_related_visit_model_cls

from edc_appointment.models import Appointment
from edc_appointment.utils import refresh_appointments
from edc_appointment_app.models import SubjectConsentV1, SubjectConsentV1Ext
from edc_appointment_app.visit_schedule import get_visit_schedule6

utc = ZoneInfo("UTC")
tz = ZoneInfo("Africa/Dar_es_Salaam")


@override_settings(SITE_ID=10)
class TestNextAppointmentCrf(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()

    @time_machine.travel(dt.datetime(2019, 6, 11, 8, 00, tzinfo=utc))
    def setUp(self):
        self.user = User.objects.create_superuser("user_login", "u@example.com", "pass")

        self.consent_v1 = ConsentDefinition(
            "edc_appointment_app.subjectconsentv1",
            version="1",
            start=ResearchProtocolConfig().study_open_datetime,
            end=ResearchProtocolConfig().study_close_datetime,
            age_min=18,
            age_is_adult=18,
            age_max=64,
            gender=[MALE, FEMALE],
        )

        consent_v1_ext = ConsentDefinitionExtension(
            "edc_appointment_app.subjectconsentv1ext",
            version="1.1",
            start=self.consent_v1.start + relativedelta(months=2),
            extends=self.consent_v1,
            timepoints=[4],
        )
        site_consents.registry = {}
        site_consents.register(self.consent_v1, extended_by=consent_v1_ext)

        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(get_visit_schedule6(self.consent_v1))
        populate_visit_schedule()

        self.subject_identifier = "101-40990029-4"
        identity = "123456789"
        self.subject_consent = SubjectConsentV1.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow() - relativedelta(days=10),
            identity=identity,
            confirm_identity=identity,
            dob=get_utcnow() - relativedelta(years=25),
        )

        # put subject on schedule
        _, schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_appointment_app.onschedulesix"
        )
        schedule.put_on_schedule(
            subject_identifier=self.subject_consent.subject_identifier,
            onschedule_datetime=self.subject_consent.consent_datetime,
        )

    @override_settings(
        EDC_APPOINTMENT_ALLOW_SKIPPED_APPT_USING={
            "edc_appointment_app.nextappointmentcrf": ("appt_date", "visitschedule")
        }
    )
    @time_machine.travel(dt.datetime(2019, 6, 11, 8, 00, tzinfo=utc))
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
        subject_visit_model_cls.objects.create(
            report_datetime=appointment.appt_datetime,
            appointment=appointment,
            reason=SCHEDULED,
        )

        traveller = time_machine.travel(appointment.appt_datetime + relativedelta(days=10))
        traveller.start()
        SubjectConsentV1Ext.objects.create(
            subject_consent=self.subject_consent,
            report_datetime=get_utcnow(),
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
            report_datetime=get_utcnow(),
            appointment=appointment,
            reason=SCHEDULED,
        )
        self.assertEqual(subject_visit.consent_version, "1.1")
