from datetime import timedelta

from django.apps import apps as django_apps
from django.test import TestCase
from django.utils import timezone

from edc_appointment.appointment_date_helper import AppointmentDateHelper
from example.models import Appointment
from example.appointment_factory import AppointmentFactory


class TestAppointmentDateHelper(TestCase):

    def setUp(self):
        self.weekday = 1
        self.appointment_date_helper = AppointmentDateHelper(Appointment)
        self.allowed_iso_weekdays = self.appointment_app_config.allowed_iso_weekdays

    @property
    def appointment_app_config(self):
        return django_apps.get_app_config('edc_appointment')

    def test_appointment_weekday_date(self):
        """Test if the  weekend datetime given returns a datetime that falls within an allowed weekday."""
        appt_datetime = timezone.datetime(2016, 7, 9, 15, 28, 22)
        allowed_iso_weekdays = [int(num) for num in str(self.allowed_iso_weekdays)]
        best_appt_datetime = self.appointment_date_helper.check_if_allowed_isoweekday(appt_datetime)
        self.assertIn(best_appt_datetime.weekday(), allowed_iso_weekdays)

    def test_appointment_weekday_date2(self):
        """Test if the  week datetime given returns a datetime that falls within an allowed weekday."""
        appt_datetime = timezone.datetime(2016, 7, 5, 15, 28, 22)
        allowed_iso_weekdays = [int(num) for num in str(self.allowed_iso_weekdays)]
        best_appt_datetime = self.appointment_date_helper.check_if_allowed_isoweekday(appt_datetime)
        self.assertIn(best_appt_datetime.weekday(), allowed_iso_weekdays)

    def test_move_on_appt_max_exceeded(self):
        """Test if the maximum number of appointment is not reached, the date will not be moved to another day."""
        original_appt_datetime = timezone.now() + timedelta(days=1)
        appointments_days_forward = 0
        appointments_per_day_max = 30
        appt_datetime = self.appointment_date_helper.move_on_appt_max_exceeded(original_appt_datetime, appointments_per_day_max, appointments_days_forward)
        self.assertEqual(appt_datetime, original_appt_datetime)

    def test_move_on_appt_max_exceeded2(self):
        """Test if the maximum number of appointment is reached, the date will be moved to another day."""
        appt_datetime = timezone.now() + timedelta(days=1)
        count = 0
        while count <= 32:
            AppointmentFactory(best_appt_datetime=appt_datetime, appt_datetime=appt_datetime)
            count += 1
        self.assertEqual(Appointment.objects.all().count(), 33)
        original_appt_datetime = appt_datetime
        appointments_days_forward = 0
        appointments_per_day_max = 30
        appt_datetime = self.appointment_date_helper.move_on_appt_max_exceeded(original_appt_datetime, appointments_per_day_max, appointments_days_forward)
        print(original_appt_datetime, "original date")
        print(appt_datetime, "#######the date ########")
