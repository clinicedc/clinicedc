from datetime import date

from django.test import TestCase

from edc_model.models import duration_to_date, InvalidFormat


class TestUtils(TestCase):
    def test_duration_to_date(self):
        reference_date = date(2015, 6, 15)
        dte = duration_to_date("5y", reference_date)
        self.assertEqual(dte, date(2010, 6, 15))
        dte = duration_to_date("5m", reference_date)
        self.assertEqual(dte, date(2015, 1, 15))
        dte = duration_to_date("5y5m", reference_date)
        self.assertEqual(dte, date(2010, 1, 15))
        self.assertRaises(InvalidFormat, duration_to_date, "5m5y", reference_date)
        self.assertRaises(InvalidFormat, duration_to_date, "m", reference_date)
        self.assertRaises(InvalidFormat, duration_to_date, "ym", reference_date)
        self.assertRaises(InvalidFormat, duration_to_date, "5y24m", reference_date)
        self.assertRaises(InvalidFormat, duration_to_date, "24m", reference_date)
        self.assertRaises(InvalidFormat, duration_to_date, "5ym", reference_date)
        self.assertRaises(InvalidFormat, duration_to_date, "y12m", reference_date)
        self.assertRaises(InvalidFormat, duration_to_date, "5y 12m", reference_date)
        self.assertRaises(InvalidFormat, duration_to_date, "5y12m ", reference_date)
        self.assertRaises(InvalidFormat, duration_to_date, " 5y12m", reference_date)
