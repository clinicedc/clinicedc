from unittest.mock import patch

from dateutil.relativedelta import relativedelta
from django.test import TestCase, override_settings
from edc_facility.import_holidays import import_holidays
from edc_protocol import Protocol
from edc_reference import site_reference_configs
from edc_visit_schedule import site_visit_schedules
from edc_visit_tracking.constants import MISSED_VISIT, SCHEDULED, UNSCHEDULED

from edc_appointment.constants import (
    COMPLETE_APPT,
    INCOMPLETE_APPT,
    MISSED_APPT,
    ONTIME_APPT,
)
from edc_appointment.creators import UnscheduledAppointmentCreator
from edc_appointment.exceptions import AppointmentWindowError
from edc_appointment.forms import AppointmentForm
from edc_appointment.models import Appointment
from edc_appointment_app.models import SubjectVisit
from edc_appointment_app.visit_schedule import visit_schedule3

from ..helper import Helper


class TestAppointmentWindowPeriod(TestCase):
    helper_cls = Helper

    @classmethod
    def setUpClass(cls):
        import_holidays()
        return super().setUpClass()

    def setUp(self):
        self.subject_identifier = "12345"
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule3)
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier,
            now=Protocol().study_open_datetime,
        )
        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "edc_appointment_app.subjectvisit"}
        )

    @staticmethod
    def create_unscheduled(appointment_1030):
        return UnscheduledAppointmentCreator(
            subject_identifier=appointment_1030.subject_identifier,
            visit_schedule_name=appointment_1030.visit_schedule_name,
            schedule_name=appointment_1030.schedule_name,
            visit_code=appointment_1030.visit_code,
            facility=appointment_1030.facility,
        ).appointment

    @staticmethod
    def get_form(appointment, appt_datetime):
        return AppointmentForm(
            data={
                "appt_datetime": appt_datetime,
                "appt_timing": ONTIME_APPT,
                "subject_identifier": appointment.subject_identifier,
                "timepoint_status": appointment.timepoint_status,
                "timepoint": appointment.timepoint,
                "timepoint_datetime": appointment.timepoint_datetime,
                "appt_close_datetime": appointment.timepoint_datetime,
                "facility_name": appointment.facility_name,
                "appt_type": appointment.appt_type,
                "appt_status": appointment.appt_status,
                "appt_reason": appointment.appt_reason,
                "document_status": appointment.document_status,
            },
            instance=appointment,
        )

    @staticmethod
    def update_appt_as_incomplete(appointment):
        appointment.refresh_from_db()
        SubjectVisit.objects.create(
            appointment=appointment,
            report_datetime=appointment.appt_datetime,
            reason=SCHEDULED if appointment.visit_code_sequence == 0 else UNSCHEDULED,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            visit_code_sequence=appointment.visit_code_sequence,
        )
        appointment.appt_status = INCOMPLETE_APPT
        appointment.save()
        appointment.refresh_from_db()

    def create_1030_and_1060(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule3",
            schedule_name="three_monthly_schedule",
        )

        appointment_1000 = Appointment.objects.get(
            subject_identifier=self.subject_identifier, visit_code="1000"
        )
        SubjectVisit.objects.create(
            appointment=appointment_1000,
            report_datetime=appointment_1000.appt_datetime,
            reason=SCHEDULED,
        )
        appointment_1000.appt_status = INCOMPLETE_APPT
        appointment_1000.save()
        appointment_1000.refresh_from_db()

        appointment_1030 = Appointment.objects.get(
            subject_identifier=self.subject_identifier, visit_code="1030"
        )
        SubjectVisit.objects.create(
            appointment=appointment_1030,
            report_datetime=appointment_1030.appt_datetime,
            reason=SCHEDULED,
        )
        appointment_1030.appt_status = INCOMPLETE_APPT
        appointment_1030.save()
        appointment_1030.refresh_from_db()
        return (
            appointment_1030,
            Appointment.objects.get(
                subject_identifier=self.subject_identifier, visit_code="1060"
            ),
        )

    def test_appointments_window_period(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule3",
            schedule_name="three_monthly_schedule",
        )
        appointments = Appointment.objects.filter(subject_identifier=self.subject_identifier)
        self.assertEqual(appointments.count(), 5)

        appointment_1030 = Appointment.objects.get(
            subject_identifier=self.subject_identifier, visit_code="1030"
        )
        appointment_1060 = Appointment.objects.get(
            subject_identifier=self.subject_identifier, visit_code="1060"
        )
        appointment_1030.appt_datetime = appointment_1060.appt_datetime
        self.assertRaises(AppointmentWindowError, appointment_1030.save)

    @patch("edc_appointment.form_validators.utils.url_names")
    def test_appointments_window_period_in_form(self, mock_urlnames):
        mock_urlnames.return_value = {"subject_dashboard_url": "subject_dashboard_url"}
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule3",
            schedule_name="three_monthly_schedule",
        )
        appointment_1030 = Appointment.objects.get(
            subject_identifier=self.subject_identifier, visit_code="1030"
        )
        appointment_1060 = Appointment.objects.get(
            subject_identifier=self.subject_identifier, visit_code="1060"
        )
        form = AppointmentForm(
            data={"appt_datetime": appointment_1060.appt_datetime},
            instance=appointment_1030,
        )
        form.is_valid()
        # conflicts on non-unique appointment date
        self.assertIn("This appointment conflicts", form._errors.get("appt_datetime")[0])
        form = AppointmentForm(
            data={"appt_datetime": appointment_1060.appt_datetime - relativedelta(days=1)},
            instance=appointment_1030,
        )
        form.is_valid()
        # outside of window period
        self.assertIn("appt_datetime", form._errors)
        self.assertIn("Invalid. Expected a date between", form._errors.get("appt_datetime")[0])

    def test_appointments_window_period_boundary_before_next_lower(self):
        appointment_1030, appointment_1060 = self.create_1030_and_1060()

        delta = appointment_1060.appt_datetime - appointment_1030.appt_datetime

        appt_datetime_before = (
            appointment_1030.appt_datetime
            + delta
            - appointment_1060.visit_from_schedule.rlower
            - relativedelta(days=1)
        )
        unscheduled_appointment = self.create_unscheduled(appointment_1030)
        form = self.get_form(unscheduled_appointment, appt_datetime_before)
        form.is_valid()
        self.assertNotIn("appt_datetime", form._errors)
        form.save()
        self.update_appt_as_incomplete(unscheduled_appointment)

    def test_appointments_window_period_boundary_on_next_lower(self):
        appointment_1030, appointment_1060 = self.create_1030_and_1060()

        delta = appointment_1060.appt_datetime - appointment_1030.appt_datetime

        appt_datetime_on = (
            appointment_1030.appt_datetime
            + delta
            - appointment_1060.visit_from_schedule.rlower
        )
        unscheduled_appointment = self.create_unscheduled(appointment_1030)
        form = self.get_form(unscheduled_appointment, appt_datetime_on)
        form.is_valid()
        self.assertIn("appt_datetime", form._errors)

    def test_appointments_window_period_boundary_after_next_lower(self):
        appointment_1030, appointment_1060 = self.create_1030_and_1060()

        delta = appointment_1060.appt_datetime - appointment_1030.appt_datetime

        appt_datetime_after = (
            appointment_1030.appt_datetime
            + delta
            - appointment_1060.visit_from_schedule.rlower
            + relativedelta(days=1)
        )
        unscheduled_appointment = self.create_unscheduled(appointment_1030)
        form = self.get_form(unscheduled_appointment, appt_datetime_after)
        form.is_valid()
        self.assertIn("appt_datetime", form._errors)

    @override_settings(EDC_APPOINTMENT_CHECK_APPT_STATUS=False)
    def test_appointments_window_period_allows_between_completed_appointments(self):
        appointment_1030, appointment_1060 = self.create_1030_and_1060()

        # assert both appointments are complete or incomplete
        appointment_1030.appt_status = INCOMPLETE_APPT
        appointment_1030.save()
        appointment_1060.appt_status = INCOMPLETE_APPT
        appointment_1060.save()
        self.assertIn(appointment_1030.appt_status, [INCOMPLETE_APPT, COMPLETE_APPT])
        self.assertIn(appointment_1060.appt_status, [INCOMPLETE_APPT, COMPLETE_APPT])

        # get appt_date one day before 1060
        appt_datetime_after_1030 = appointment_1060.appt_datetime - relativedelta(days=1)
        # create unscheduled off of 1030
        unscheduled_appointment = self.create_unscheduled(appointment_1030)

        # set appt_date to  one day before 1060
        form = self.get_form(unscheduled_appointment, appt_datetime_after_1030)
        form.is_valid()
        self.assertNotIn("appt_datetime", form._errors)

    def test_appointments_window_period_does_not_allow_between_new_appointments(self):
        appointment_1030, appointment_1060 = self.create_1030_and_1060()

        # assert only appointment_1030 is complete / incomplete
        appointment_1030.appt_status = INCOMPLETE_APPT
        appointment_1030.save()
        self.assertIn(appointment_1030.appt_status, [INCOMPLETE_APPT, COMPLETE_APPT])
        self.assertNotIn(
            appointment_1060.appt_status, [INCOMPLETE_APPT, COMPLETE_APPT, MISSED_APPT]
        )

        # get appt_date one day before 1060
        appt_datetime_after_1030 = appointment_1060.appt_datetime - relativedelta(days=1)
        # create unscheduled off of 1030
        unscheduled_appointment = self.create_unscheduled(appointment_1030)

        # set appt_date to  one day before 1060
        form = self.get_form(unscheduled_appointment, appt_datetime_after_1030)
        form.is_valid()
        self.assertIn("appt_datetime", form._errors)

    @override_settings(EDC_APPOINTMENT_CHECK_APPT_STATUS=False)
    def test_appointments_window_period_does_not_allow_missed_unscheduled(self):
        """Assert does not allow an unscheduled appointment if the
        scheduled appt is missed (in this case 1030 is missed)
        """
        appointment_1030, appointment_1060 = self.create_1030_and_1060()

        appointment_1030.appt_timing = MISSED_APPT
        appointment_1030.save()
        appointment_1030.refresh_from_db()

        subject_visit = SubjectVisit.objects.get(appointment=appointment_1030)
        subject_visit.reason = MISSED_VISIT
        subject_visit.save()
        subject_visit.refresh_from_db()

        appointment_1030.appt_status = INCOMPLETE_APPT
        appointment_1030.save()
        appointment_1030.refresh_from_db()

        self.assertIn(subject_visit.reason, [MISSED_VISIT])
        self.assertIn(appointment_1030.appt_timing, [MISSED_APPT])
        self.assertIn(appointment_1030.appt_status, [INCOMPLETE_APPT])

        # get appt_date one day before 1060
        appt_datetime_after_1030 = appointment_1060.appt_datetime - relativedelta(days=1)
        # create unscheduled off of 1030
        unscheduled_appointment = self.create_unscheduled(appointment_1030)

        # set appt_date to  one day before 1060
        form = self.get_form(unscheduled_appointment, appt_datetime_after_1030)
        form.is_valid()
        self.assertIn("appt_datetime", form._errors)
