from django.test import TestCase, tag
from edc_appointment.forms import AppointmentForm
from edc_appointment.model_mixins.appointment_model_mixin import AppointmentWindowError
from edc_protocol import Protocol
from edc_facility.import_holidays import import_holidays
from edc_visit_schedule import site_visit_schedules

from ..models import Appointment
from .helper import Helper
from .visit_schedule import visit_schedule1, visit_schedule2, visit_schedule3


class TestAppointment(TestCase):
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

    @tag("appt")
    def test_appointments_window_period(self):
        """Assert appointment triggering method creates appointments.
        """
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule3",
            schedule_name="three_monthly_schedule",
        )
        appointments = Appointment.objects.filter(
            subject_identifier=self.subject_identifier
        )
        self.assertEqual(appointments.count(), 5)

        appointment_1030 = Appointment.objects.get(
            subject_identifier=self.subject_identifier, visit_code="1030"
        )
        appointment_1060 = Appointment.objects.get(
            subject_identifier=self.subject_identifier, visit_code="1060"
        )
        appointment_1030.appt_datetime = appointment_1060.appt_datetime
        self.assertRaises(AppointmentWindowError, appointment_1030.save)

        form = AppointmentForm(
            data={"appt_datetime": appointment_1060.appt_datetime},
            instance=appointment_1030,
        )
        form.is_valid()
        self.assertIn("__all__", form._errors)
        self.assertIn("Invalid appointment date", form._errors.get("__all__")[0])
