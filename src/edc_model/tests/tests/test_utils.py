from datetime import date, datetime

from django import forms
from django.test import TestCase, override_settings
from pytz import UTC

from edc_model.utils import (
    InvalidFieldName,
    InvalidFormat,
    duration_to_date,
    estimated_date_from_ago,
)

from ..models import SimpleModel


class TestUtils(TestCase):
    def test_duration_to_date(self):
        reference_date = date(2015, 6, 15)
        dte = duration_to_date("5y", reference_date)
        self.assertEqual(dte, date(2010, 6, 15))
        dte = duration_to_date("5m", reference_date)
        self.assertEqual(dte, date(2015, 1, 15))
        dte = duration_to_date("5y5m", reference_date)
        self.assertEqual(dte, date(2010, 1, 15))
        dte = duration_to_date("5y 5m", reference_date)
        self.assertEqual(dte, date(2010, 1, 15))
        self.assertRaises(InvalidFormat, duration_to_date, "5m5y", reference_date)
        self.assertRaises(InvalidFormat, duration_to_date, "m", reference_date)
        self.assertRaises(InvalidFormat, duration_to_date, "ym", reference_date)
        self.assertRaises(InvalidFormat, duration_to_date, "5y24m", reference_date)
        self.assertRaises(InvalidFormat, duration_to_date, "24m", reference_date)
        self.assertRaises(InvalidFormat, duration_to_date, "5ym", reference_date)
        self.assertRaises(InvalidFormat, duration_to_date, "y12m", reference_date)
        # self.assertRaises(InvalidFormat, duration_to_date, "5y 12m", reference_date)
        # self.assertRaises(InvalidFormat, duration_to_date, "5y12m ", reference_date)
        # self.assertRaises(InvalidFormat, duration_to_date, " 5y12m", reference_date)

    def test_duration_to_date_with_day(self):
        reference_date = date(2015, 6, 15)
        dte = duration_to_date("5d", reference_date)
        self.assertEqual(dte, date(2015, 6, 10))
        self.assertRaises(InvalidFormat, duration_to_date, " d", reference_date)
        self.assertRaises(InvalidFormat, duration_to_date, " 5m12d", reference_date)
        self.assertRaises(InvalidFormat, duration_to_date, " 5y12d", reference_date)
        self.assertRaises(InvalidFormat, duration_to_date, " 5y9m12d", reference_date)

    def test_duration_to_future_date(self):
        reference_date = date(2015, 6, 15)
        dte = duration_to_date("5d", reference_date, future=True)
        self.assertEqual(dte, date(2015, 6, 20))

    @override_settings(REPORT_DATETIME_FIELD_NAME="report_datetime")
    def test_estimated_date_from_ago(self):
        reference_date = date(2015, 6, 15)
        dte = duration_to_date("5d", reference_date, future=True)
        cleaned_data = {"dx_ago": "5d", "report_datetime": reference_date}
        estimated_date = estimated_date_from_ago(cleaned_data, "dx_ago", future=True)
        self.assertEqual(dte, estimated_date)

        cleaned_data = {"dx_ago": "md", "report_datetime": reference_date}
        self.assertRaises(
            forms.ValidationError, estimated_date_from_ago, cleaned_data, "dx_ago", future=True
        )

        self.assertRaises(
            InvalidFieldName,
            estimated_date_from_ago,
            cleaned_data,
            "dx_ago_blah",
        )

        reference_datetime = datetime(2015, 6, 15, tzinfo=UTC)
        obj = SimpleModel.objects.create(ago="5d", report_datetime=reference_datetime)
        estimated_date = estimated_date_from_ago(obj, "ago", future=True)
        self.assertEqual(estimated_date, date(2015, 6, 20))

        reference_date = datetime(2015, 6, 15)
        obj = SimpleModel.objects.create(ago="5d", d1=reference_date)
        estimated_date = estimated_date_from_ago(obj, "ago", reference_field="d1", future=True)
        self.assertEqual(estimated_date, date(2015, 6, 20))

        obj = SimpleModel.objects.create(ago="5m6d", d1=reference_date)
        self.assertRaises(
            InvalidFormat,
            estimated_date_from_ago,
            obj,
            "ago",
            reference_field="d1",
            future=True,
        )

        obj = SimpleModel.objects.create(ago=None, d1=reference_date)
        estimated_date = estimated_date_from_ago(obj, "ago", reference_field="d1", future=True)
        self.assertIsNone(estimated_date)

        obj = SimpleModel.objects.create(ago=None, d1=None)
        estimated_date = estimated_date_from_ago(obj, "ago", reference_field="d1", future=True)
        self.assertIsNone(estimated_date)

        obj = SimpleModel.objects.create(ago=None)
        estimated_date = estimated_date_from_ago(obj, "ago")
        self.assertIsNone(estimated_date)

        obj = SimpleModel.objects.create(ago="5d", report_datetime=reference_datetime)
        self.assertRaises(InvalidFieldName, estimated_date_from_ago, obj, "ago_blah")

        self.assertRaises(InvalidFieldName, estimated_date_from_ago, obj, "")

        self.assertRaises(InvalidFieldName, estimated_date_from_ago, obj, None)
