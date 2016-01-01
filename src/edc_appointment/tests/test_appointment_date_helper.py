from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta

from edc_configuration.models import GlobalConfiguration
from edc_appointment.models import Appointment, AppointmentDateHelper

from .base_test_case import BaseTestCase


class TestAppointmentDateHelper(BaseTestCase):

    def test_check_if_allowed_isoweekday(self):
        obj = GlobalConfiguration.objects.get(attribute='allowed_iso_weekdays')
        obj.value = '12345'
        obj.save()
        date_helper = AppointmentDateHelper(Appointment)
        self.assertEqual(date_helper.allowed_iso_weekdays, obj.value)
        for days in range(0, 30):
            dte = datetime.today() + timedelta(days=days)
            new_dte = date_helper._check_if_allowed_isoweekday(dte)
            self.assertTrue(new_dte.isoweekday not in [int(x) for x in date_helper.allowed_iso_weekdays])
            self.assertTrue(
                new_dte.strftime('%A') not in [
                    'Saturday', 'Sunday'], '{0} is in {1}'.format(new_dte.strftime('%A'), ['Saturday', 'Sunday']))

    def test_change_allowed_iso_weekdays(self):
        """Asserts cannot return an iso weekday outside of allowed iso weekdays"""
        obj = GlobalConfiguration.objects.get(attribute='allowed_iso_weekdays')
        obj.value = '67'
        obj.save()
        date_helper = AppointmentDateHelper(Appointment)
        self.assertEqual(date_helper.allowed_iso_weekdays, obj.value)
        for days in range(0, 30):
            dte = datetime.today() + timedelta(days=days)
            new_dte = date_helper._check_if_allowed_isoweekday(dte)
            self.assertTrue(new_dte.isoweekday not in [int(x) for x in date_helper.allowed_iso_weekdays])
            self.assertTrue(
                new_dte.strftime('%A') in [
                    'Saturday', 'Sunday'], '{0} is not in {1}'.format(new_dte.strftime('%A'), ['Saturday', 'Sunday']))

    def test_move_to_same_weekday(self):
        """Asserts appt_date stays on same day"""
        obj = GlobalConfiguration.objects.get(attribute='allowed_iso_weekdays')
        obj.value = '12345'
        obj.save()
        obj = GlobalConfiguration.objects.get(attribute='use_same_weekday')
        obj.value = True
        obj.save()
        date_helper = AppointmentDateHelper(Appointment)
        self.assertTrue(date_helper.use_same_weekday)
        weekday = 1
        for interval in range(0, 12):
            base_datetime = datetime.today() - timedelta(days=30)
            while True:
                if base_datetime.isoweekday() != weekday:
                    base_datetime += timedelta(days=1)
                else:
                    break
            dte = base_datetime + relativedelta(months=interval)
            new_dte = date_helper._check_if_allowed_isoweekday(dte)
            self.assertTrue(new_dte.isoweekday not in [int(x) for x in date_helper.allowed_iso_weekdays])
            newer_dte = date_helper._move_to_same_weekday(new_dte, weekday)
            self.assertTrue(newer_dte.strftime('%A') == base_datetime.strftime('%A'))

        # confirm appt_date does not necessarily stay on same day
        obj = GlobalConfiguration.objects.get(attribute='use_same_weekday')
        obj.value = False
        obj.save()
        date_helper = AppointmentDateHelper(Appointment)
        self.assertFalse(date_helper.use_same_weekday)
        dow = []
        for interval in range(0, 12):
            base_datetime = datetime.today() - timedelta(days=30)
            while True:
                if base_datetime.isoweekday() != weekday:
                    base_datetime += timedelta(days=1)
                else:
                    break
            dte = base_datetime + relativedelta(months=interval)
            new_dte = date_helper._check_if_allowed_isoweekday(dte)
            self.assertTrue(new_dte.isoweekday not in [int(x) for x in date_helper.allowed_iso_weekdays])
            newer_dte = date_helper._move_to_same_weekday(new_dte, weekday)
            dow.append(newer_dte.strftime('%A'))
        self.assertTrue(len(list(set(dow))) > 1)
