from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from django.conf import settings
from django.test.utils import override_settings
from edc_consent.consent_definition import ConsentDefinition
from edc_consent.site_consents import site_consents
from edc_constants.constants import FEMALE, MALE
from edc_facility.import_holidays import import_holidays

from edc_appointment.creators import AppointmentCreator
from edc_appointment.models import Appointment
from edc_appointment.tests.tests.test_appointment_creator import (
    AppointmentCreatorTestCase,
)

utc_tz = ZoneInfo("UTC")


@time_machine.travel(datetime(1900, 1, 11, 0, 00, tzinfo=utc_tz))
class TestAppointmentCreator2(AppointmentCreatorTestCase):
    @override_settings(
        HOLIDAY_FILE=settings.BASE_DIR / "no_holidays.csv",
        EDC_PROTOCOL_STUDY_OPEN_DATETIME=datetime(1900, 1, 1, 0, 0, 0, tzinfo=utc_tz),
        EDC_PROTOCOL_STUDY_CLOSE_DATETIME=datetime(1901, 10, 2, 0, 0, 0, tzinfo=utc_tz),
    )
    def test_create_no_holidays(self):
        """test create appointment, no holiday to avoid after 1900"""
        import_holidays()
        appt_datetime = datetime(1900, 1, 1, tzinfo=ZoneInfo("UTC"))
        site_consents.registry = {}
        consent_definition = ConsentDefinition(
            "edc_appointment_app.subjectconsentv1",
            version="1",
            start=datetime(1900, 1, 1, 0, 0, 0, tzinfo=utc_tz),
            end=datetime(1901, 10, 2, 0, 0, 0, tzinfo=utc_tz),
            age_min=18,
            age_is_adult=18,
            age_max=64,
            gender=[MALE, FEMALE],
        )
        site_consents.register(consent_definition)
        self.put_on_schedule(appt_datetime, consent_definition=consent_definition)

        expected_appt_datetime = datetime(1900, 1, 2, tzinfo=ZoneInfo("UTC"))
        creator = AppointmentCreator(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            visit=self.visit1000,
            timepoint_datetime=appt_datetime,
        )
        self.assertEqual(
            Appointment.objects.all().order_by("timepoint", "visit_code_sequence")[0],
            creator.appointment,
        )
        self.assertEqual(
            Appointment.objects.all()
            .order_by("timepoint", "visit_code_sequence")[0]
            .appt_datetime,
            expected_appt_datetime,
        )

        appt_datetime = datetime(1900, 1, 3, tzinfo=ZoneInfo("UTC"))
        creator = AppointmentCreator(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            visit=self.visit1000,
            timepoint_datetime=appt_datetime,
        )
        self.assertEqual(
            Appointment.objects.all().order_by("timepoint", "visit_code_sequence")[0],
            creator.appointment,
        )
        self.assertEqual(
            Appointment.objects.all()
            .order_by("timepoint", "visit_code_sequence")[0]
            .appt_datetime,
            appt_datetime,
        )
