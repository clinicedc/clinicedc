from datetime import timedelta, datetime

from dateutil.relativedelta import relativedelta

from django.test import TestCase

from ..classes import AppointmentDateHelper


class AppointmentHelperTests(TestCase):

    def test_check_if_allowed_isoweekday(self):
        configuration.allowed_iso_weekdays = '12345'
        date_helper = AppointmentDateHelper()

        print 'confirm cannot return an iso weekday outside of {0}'.format(configuration.allowed_iso_weekdays)
        for days in range(0, 30):
            dte = datetime.today() + timedelta(days=days)
            new_dte = date_helper._check_if_allowed_isoweekday(dte)
            self.assertTrue(new_dte.isoweekday not in [int(x) for x in configuration.allowed_iso_weekdays])
            self.assertTrue(new_dte.strftime('%A') not in ['Saturday', 'Sunday'], '{0} is in {1}'.format(new_dte.strftime('%A'), ['Saturday', 'Sunday']))

        print 'change allowed_iso_weekdays to 67'
        configuration.allowed_iso_weekdays = '67'
        configuration.save()
        date_helper.allowed_iso_weekdays = configuration.allowed_iso_weekdays
        print 'confirm cannot return an iso weekday outside of {0}'.format(configuration.allowed_iso_weekdays)
        for days in range(0, 30):
            dte = datetime.today() + timedelta(days=days)
            new_dte = date_helper._check_if_allowed_isoweekday(dte)
            self.assertTrue(new_dte.isoweekday not in [int(x) for x in configuration.allowed_iso_weekdays])
            self.assertTrue(new_dte.strftime('%A') in ['Saturday', 'Sunday'], '{0} is not in {1}'.format(new_dte.strftime('%A'), ['Saturday', 'Sunday']))

    def test_move_to_same_weekday(self):
        """Test _move_to_same_weekday."""
        configuration.allowed_iso_weekdays = '12345'
        configuration.use_same_weekday = True
        weekday = 1
        date_helper = AppointmentDateHelper()
        print 'confirm appt_date stays on same day'
        for interval in range(0, 12):
            base_datetime = datetime.today() - timedelta(days=30)
            while True:
                if base_datetime.isoweekday() != weekday:
                    base_datetime += timedelta(days=1)
                else:
                    break
            dte = base_datetime + relativedelta(months=interval)
            new_dte = date_helper._check_if_allowed_isoweekday(dte)
            self.assertTrue(new_dte.isoweekday not in [int(x) for x in configuration.allowed_iso_weekdays])
            newer_dte = date_helper._move_to_same_weekday(new_dte, weekday)
            print 'was {0}, then {1}, and finally {2}, which is a {3}'.format(dte, new_dte, newer_dte, newer_dte.strftime('%A'))
            self.assertTrue(newer_dte.strftime('%A') == base_datetime.strftime('%A'))

        print 'confirm appt_date does not necessarily stay on same day'
        configuration.use_same_weekday = False
        configuration.save()
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
            self.assertTrue(new_dte.isoweekday not in [int(x) for x in configuration.allowed_iso_weekdays])
            newer_dte = date_helper._move_to_same_weekday(new_dte, weekday)
            print 'was {0}, then {1}, and finally {2}, which is a {3}'.format(dte, new_dte, newer_dte, newer_dte.strftime('%A'))
            dow.append(newer_dte.strftime('%A'))
        self.assertTrue(len(list(set(dow))) > 1)
