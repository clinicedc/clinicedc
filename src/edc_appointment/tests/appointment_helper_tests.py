from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta

from ..models import AppointmentDateHelper

from .base_test_case import BaseTestCase


class AppointmentHelperTests(BaseTestCase):

    def test_check_if_allowed_isoweekday(self):
        self.configuration.allowed_iso_weekdays = '12345'
        date_helper = AppointmentDateHelper()
        for days in range(0, 30):
            dte = datetime.today() + timedelta(days=days)
            new_dte = date_helper._check_if_allowed_isoweekday(dte)
            self.assertTrue(new_dte.isoweekday not in [int(x) for x in self.configuration.allowed_iso_weekdays])
            self.assertTrue(
                new_dte.strftime('%A') not in [
                    'Saturday', 'Sunday'], '{0} is in {1}'.format(new_dte.strftime('%A'), ['Saturday', 'Sunday']))

    def test_change_allowed_iso_weekdays(self):
        """Asserts cannot return an iso weekday outside of allowed iso weekdays"""
        self.configuration.allowed_iso_weekdays = '67'
        self.configuration.save()
        date_helper = AppointmentDateHelper()
        date_helper.allowed_iso_weekdays = self.configuration.allowed_iso_weekdays
        for days in range(0, 30):
            dte = datetime.today() + timedelta(days=days)
            new_dte = date_helper._check_if_allowed_isoweekday(dte)
            self.assertTrue(new_dte.isoweekday not in [int(x) for x in self.configuration.allowed_iso_weekdays])
            self.assertTrue(
                new_dte.strftime('%A') in [
                    'Saturday', 'Sunday'], '{0} is not in {1}'.format(new_dte.strftime('%A'), ['Saturday', 'Sunday']))

    def test_move_to_same_weekday(self):
        """Asserts appt_date stays on same day"""
        self.configuration.allowed_iso_weekdays = '12345'
        self.configuration.use_same_weekday = True
        weekday = 1
        date_helper = AppointmentDateHelper()
        for interval in range(0, 12):
            base_datetime = datetime.today() - timedelta(days=30)
            while True:
                if base_datetime.isoweekday() != weekday:
                    base_datetime += timedelta(days=1)
                else:
                    break
            dte = base_datetime + relativedelta(months=interval)
            new_dte = date_helper._check_if_allowed_isoweekday(dte)
            self.assertTrue(new_dte.isoweekday not in [int(x) for x in self.configuration.allowed_iso_weekdays])
            newer_dte = date_helper._move_to_same_weekday(new_dte, weekday)
            self.assertTrue(newer_dte.strftime('%A') == base_datetime.strftime('%A'))

        # confirm appt_date does not necessarily stay on same day
        self.configuration.use_same_weekday = False
        self.configuration.save()
        date_helper.use_same_weekday = False
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
            self.assertTrue(new_dte.isoweekday not in [int(x) for x in self.configuration.allowed_iso_weekdays])
            newer_dte = date_helper._move_to_same_weekday(new_dte, weekday)
            dow.append(newer_dte.strftime('%A'))
        self.assertTrue(len(list(set(dow))) > 1)
