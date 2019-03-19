import arrow
import pytz

from datetime import datetime, date
from dateutil import tz

# from django.test import TestCase, tag  # noqa
from unittest import TestCase

from edc_utils import (
    age,
    formatted_age,
    formatted_datetime,
    get_age_in_days,
    get_safe_random_string,
    AgeValueError,
    get_dob,
)


class TestUtils(TestCase):
    def test_get_safe_random_string(self):
        """With default parameters"""
        _safe_string = get_safe_random_string()
        allowed_chars = "ABCDEFGHKMNPRTUVWXYZ2346789"
        for character in _safe_string:
            if character not in allowed_chars:
                assert False

    def test_formatted_age(self):

        self.assertEqual(
            formatted_age(None, pytz.utc.localize(datetime(2016, 12, 12))), "?"
        )

        self.assertEqual(
            formatted_age(
                date(1990, 12, 12), pytz.utc.localize(datetime(2016, 12, 12))
            ),
            "26y",
        )
        self.assertEqual(
            formatted_age(date(2016, 9, 9), pytz.utc.localize(datetime(2016, 12, 12))),
            "3m",
        )
        self.assertEqual(
            formatted_age(
                date(2016, 10, 28), pytz.utc.localize(datetime(2016, 12, 12))
            ),
            "1m14d",
        )
        self.assertEqual(
            formatted_age(date(2016, 12, 6), pytz.utc.localize(datetime(2016, 12, 12))),
            "6d",
        )
        self.assertEqual(
            formatted_age(
                date(2015, 12, 12), pytz.utc.localize(datetime(2016, 12, 12))
            ),
            "12m",
        )

        self.assertRaises(
            AgeValueError,
            formatted_age,
            date(2016, 12, 12),
            pytz.utc.localize(datetime(2015, 12, 12)),
        )

    def test_age_in_days(self):
        born = date(2016, 10, 20)
        reference_date = pytz.utc.localize(datetime(2016, 10, 28))
        self.assertEqual(get_age_in_days(reference_date, born), 8)

    def test_age(self):
        born = date(1990, 5, 1)
        reference_dt = pytz.utc.localize(datetime(2000, 5, 1))
        self.assertEqual(age(born, reference_dt).years, 10)

        self.assertEqual(get_dob(age_in_years=10, now=reference_dt), born)
        self.assertEqual(get_dob(age_in_years=10, now=reference_dt.date()), born)

    def test_age_without_tz(self):
        born = pytz.utc.localize(datetime(1990, 5, 1))
        reference_dt = datetime(2000, 5, 1)
        self.assertEqual(age(born, reference_dt).years, 10)

    def test_age_born_date(self):
        born = date(1990, 5, 1)
        reference_dt = datetime(2000, 5, 1)
        self.assertEqual(age(born, reference_dt).years, 10)

    def test_age_reference_as_date(self):
        born = pytz.utc.localize(datetime(1990, 5, 1))
        reference_dt = date(2000, 5, 1)
        self.assertEqual(age(born, reference_dt).years, 10)

    def test_age_zero1(self):
        """Assert born precedes reference considering timezones."""
        born = arrow.get(
            datetime(1990, 5, 1, 0, 0), tz.gettz("Africa/Gaborone")
        ).datetime
        reference_dt = arrow.get(datetime(1990, 5, 1, 0, 0), tz.gettz("UTC")).datetime
        self.assertEqual(age(born, reference_dt).years, 0)

    def test_age_zero2(self):
        """Assert born == reference considering timezones."""
        born = arrow.get(
            datetime(1990, 5, 1, 2, 0), tz.gettz("Africa/Gaborone")
        ).datetime
        reference_dt = arrow.get(datetime(1990, 5, 1, 0, 0), tz.gettz("UTC")).datetime
        self.assertEqual(age(born, reference_dt).hours, 0)

    def test_age_zero3(self):
        """Assert born after reference date considering timezones."""
        born = arrow.get(
            datetime(1990, 5, 2, 5, 0), tz.gettz("Africa/Gaborone")
        ).datetime
        reference_dt = arrow.get(datetime(1990, 5, 2, 2, 0), tz.gettz("UTC")).datetime
        self.assertRaises(AgeValueError, age, born, reference_dt)

    def test_age_zero4(self):
        """Assert born 2hrs before reference date considering timezones."""
        born = arrow.get(
            datetime(1990, 5, 2, 0, 0), tz.gettz("Africa/Gaborone")
        ).datetime
        reference_dt = arrow.get(
            datetime(1990, 5, 2, 2, 0), tz.gettz("Africa/Gaborone")
        ).datetime
        self.assertEqual(age(born, reference_dt).hours, 2)

    def test_age_zero5(self):
        """Assert born 8hrs before reference date considering timezones."""
        born = arrow.get(datetime(1990, 5, 2, 0, 0), tz.gettz("Africa/Gaborone"))
        reference_dt = arrow.get(
            datetime(1990, 5, 2, 2, 0), tz.gettz("America/New_York")
        )
        dst = reference_dt.dst()
        seconds = dst.days * 24 * 60 * 60 + dst.seconds
        dst_hours, _ = divmod(seconds, 3600)
        self.assertEqual(
            age(born.datetime, reference_dt.datetime).hours, 7 + 2 - dst_hours
        )

    def test_formatted_datetime(self):
        born = arrow.get(
            datetime(1990, 5, 2, 0, 0), tz.gettz("Africa/Gaborone")
        ).datetime
        self.assertTrue(formatted_datetime(born))
