from datetime import timedelta, datetime

from django.apps import apps as django_apps
from django.test import TestCase
from django.utils import timezone

from edc_appointment.appointment_date_helper import AppointmentDateHelper
from edc_example.models import Appointment
from edc_appointment.models import Holiday


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

#     def test_move_on_appt_max_exceeded(self):
#         """Test if the maximum number of appointment is not reached, the date will not be moved to another day."""
#         original_appt_datetime = timezone.now() + timedelta(days=1)
#         appointments_days_forward = 0
#         appointments_per_day_max = 30
#         appt_datetime = self.appointment_date_helper.move_on_appt_max_exceeded(
#             original_appt_datetime, appointments_per_day_max, appointments_days_forward)
#         self.assertEqual(appt_datetime, original_appt_datetime)

#     def test_move_on_appt_max_exceeded2(self):
#         """Test if the maximum number of appointment is reached, the date will be moved to another day."""
#         appt_datetime = timezone.now() + timedelta(days=2)
#         expected_appt_datetime = timezone.now() + timedelta(days=2)
#         expected_datetime = datetime(
#             expected_appt_datetime.year,
#             expected_appt_datetime.month,
#             expected_appt_datetime.day,
#             appt_datetime.hour,
#             appt_datetime.minute)
#         count = 0
#         while count <= 32:
#             AppointmentFactory(best_appt_datetime=appt_datetime, appt_datetime=appt_datetime)
#             count += 1
#         self.assertEqual(Appointment.objects.all().count(), 33)
#         original_appt_datetime = appt_datetime
#         appointments_days_forward = 30
#         appointments_per_day_max = 30
#         appt_datetime = self.appointment_date_helper.move_on_appt_max_exceeded(
#             original_appt_datetime, appointments_per_day_max, appointments_days_forward)
#         self.assertEqual(appt_datetime, expected_datetime)

    def test_move_appt_to_same_weekday(self):
        """Test if a datetime given is moved to the same weekday given."""
        week = 2
        appt_datetime = timezone.datetime(2016, 7, 22, 6, 59, 25)
        expected_appt_datetime = timezone.datetime(2016, 7, 19, 6, 59, 25)
        appt_datetime = self.appointment_date_helper.move_appt_to_same_weekday(appt_datetime, week)
        self.assertEqual(appt_datetime, expected_appt_datetime)

    def test_check_if_holiday(self):
        """Test if an appointment is a holiday is moved to the next 2 days."""
        appt_datetime = timezone.datetime(2016, 7, 30, 12, 47) + timedelta(days=+2)
        expected_appt_datetime = timezone.datetime(2016, 7, 30, 12, 47) + timedelta(days=+3)
        Holiday.objects.create(
            holiday_date=appt_datetime.date(),
            holiday_name="public holiday")
        new_appt_datetime = self.appointment_date_helper.check_if_holiday(appt_datetime)
        appt_datetime.hour, appt_datetime.minute
        self.assertEqual(new_appt_datetime, expected_appt_datetime)

    def testcheck_appt_date(self):
        """Test if given an appointment date time that is not a holiday, allowed isoweekday and maximum appointments,

         not reached for that date returns the same date time given."""
        appt_datetime = timezone.datetime(2016, 7, 26, 12, 47)
        new_appt_datetime = self.appointment_date_helper.check_appt_date(appt_datetime)
        self.assertEqual(new_appt_datetime, appt_datetime)

    def testcheck_appt_date2(self):
        """Test if given an appointment date time that is a holiday, allowed isoweekday and maximum appointments,

         not reached for that date returns a different date time given."""
        appt_datetime = timezone.datetime(2016, 7, 26, 12, 47)
        Holiday.objects.create(
            holiday_date=appt_datetime.date(),
            holiday_name="public holiday")
        expected_appt_datetime = timezone.datetime(2016, 7, 26, 12, 47) + timedelta(days=+1)
        new_appt_datetime = self.appointment_date_helper.check_appt_date(appt_datetime)
        self.assertEqual(new_appt_datetime, expected_appt_datetime)

    def testcheck_appt_date3(self):
        """Test if given an appointment date time that not is a holiday, not allowed isoweekday and maximum

         appointments, not reached for that date returns a different date time given."""
        appt_datetime = timezone.datetime(2016, 7, 30, 12, 47)
        expected_appt_datetime = timezone.datetime(2016, 7, 30, 12, 47) + timedelta(days=-1)
        new_appt_datetime = self.appointment_date_helper.check_appt_date(appt_datetime)
        self.assertEqual(new_appt_datetime, expected_appt_datetime)
