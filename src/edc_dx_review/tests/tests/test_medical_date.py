from dateutil.relativedelta import relativedelta
from django.test import TestCase
from edc_utils import get_utcnow

from edc_dx_review.medical_date import (
    BEFORE_AFTER_BOTH_FALSE,
    BEFORE_AFTER_BOTH_TRUE,
    FAILED_COMPARISON,
    DxDate,
    MedicalDate,
    MedicalDateError,
    RxDate,
)


class TestMedicalDate(TestCase):
    def test_medical_date_error(self):
        cleaned_data = {
            "report_datetime": get_utcnow(),
            "medical_ago": "1y",
        }
        opts = dict(
            after_reference=True,
            reference_date=cleaned_data.get("report_datetime"),
            reference_is_none_msg="Complete the report date.",
            inclusive=True,
            label="medical",
        )
        with self.assertRaises(MedicalDateError) as cm:
            MedicalDate("medical_date", "medical_ago", cleaned_data, **opts)
        self.assertIn("medical_ago", cm.exception.message_dict)
        self.assertIn(
            "Medical date must be on or after",
            str([value for value in cm.exception.message_dict.values()]),
        )
        self.assertEqual(FAILED_COMPARISON, cm.exception.code)

    def test_medical_date(self):
        cleaned_data = {
            "report_datetime": get_utcnow(),
            "medical_date": (get_utcnow() - relativedelta(years=1)),
        }
        opts = dict(
            before_reference=True,
            reference_date=cleaned_data.get("report_datetime"),
            reference_is_none_msg="Complete the report date.",
            inclusive=True,
            label="medical",
        )
        try:
            MedicalDate("medical_date", "medical_ago", cleaned_data, **opts)
        except MedicalDateError as e:
            self.fail(f"Exception unexpectedly raised. Got {e}.")

        cleaned_data = {
            "report_datetime": get_utcnow(),
            "medical_ago": "1y",
        }
        MedicalDate("medical_date", "medical_ago", cleaned_data, **opts)

        cleaned_data = {
            "report_datetime": get_utcnow(),
            "medical_ago": "1y",
        }
        opts.update(before_reference=False)
        with self.assertRaises(MedicalDateError) as cm:
            MedicalDate("medical_date", "medical_ago", cleaned_data, **opts)
        self.assertIn("supposed to be before or after", str(cm.exception))

        cleaned_data = {
            "report_datetime": get_utcnow(),
            "medical_date": get_utcnow(),
        }
        opts.update(before_reference=True, inclusive=False)
        with self.assertRaises(MedicalDateError) as cm:
            MedicalDate("medical_date", "medical_ago", cleaned_data, **opts)
        self.assertEqual(FAILED_COMPARISON, cm.exception.code)

        opts.update(before_reference=False, after_reference=True, inclusive=False)
        with self.assertRaises(MedicalDateError) as cm:
            MedicalDate("medical_date", "medical_ago", cleaned_data, **opts)
        self.assertEqual(FAILED_COMPARISON, cm.exception.code)

        opts.update(before_reference=True, after_reference=True, inclusive=False)
        with self.assertRaises(MedicalDateError) as cm:
            MedicalDate("medical_date", "medical_ago", cleaned_data, **opts)
        self.assertEqual(BEFORE_AFTER_BOTH_TRUE, cm.exception.code)

        opts.update(before_reference=False, after_reference=False, inclusive=False)
        with self.assertRaises(MedicalDateError) as cm:
            MedicalDate("medical_date", "medical_ago", cleaned_data, **opts)
        self.assertEqual(BEFORE_AFTER_BOTH_FALSE, cm.exception.code)

        cleaned_data = {
            "report_datetime": get_utcnow(),
            "medical_date": get_utcnow() + relativedelta(days=1),
        }
        opts.update(before_reference=False, after_reference=True, inclusive=True)
        try:
            MedicalDate("medical_date", "medical_ago", cleaned_data, **opts)
        except MedicalDateError as e:
            self.fail(f"Exception unexpectedly raised. Got {e}")

    def test_dx_date(self):
        cleaned_data = {}
        with self.assertRaises(MedicalDateError) as cm:
            DxDate(cleaned_data)
        self.assertIn("Complete the report date", str(cm.exception))

        cleaned_data = {"report_datetime": None}
        with self.assertRaises(MedicalDateError) as cm:
            DxDate(cleaned_data)
        self.assertIn("Complete the report date", str(cm.exception))

        cleaned_data = {"report_datetime": get_utcnow()}
        with self.assertRaises(MedicalDateError) as cm:
            DxDate(cleaned_data)
        self.assertIn("Complete the diagnosis date", str(cm.exception))

        cleaned_data = {"report_datetime": get_utcnow(), "dx_ago": None}
        with self.assertRaises(MedicalDateError) as cm:
            DxDate(cleaned_data)
        self.assertIn("Complete the diagnosis date", str(cm.exception))

        cleaned_data = {"report_datetime": get_utcnow(), "dx_ago": "1y"}
        try:
            DxDate(cleaned_data)
        except MedicalDateError as e:
            self.fail(f"Exception unexpectedly raised. Got{e}")

        cleaned_data = {
            "report_datetime": get_utcnow() - relativedelta(years=2),
            "dx_date": get_utcnow().date(),
        }
        with self.assertRaises(MedicalDateError) as cm:
            DxDate(cleaned_data)
        self.assertIn("date must be on or before", str(cm.exception))

        cleaned_data = {
            "report_datetime": get_utcnow(),
            "dx_date": get_utcnow().date() - relativedelta(years=3),
        }
        try:
            DxDate(cleaned_data)
        except MedicalDateError as e:
            self.fail(f"Exception unexpectedly raised. Got{e}")

        cleaned_data = {
            "report_datetime": get_utcnow(),
            "dx_date": get_utcnow().date() - relativedelta(years=3),
            "dx_ago": "1y",
        }
        with self.assertRaises(MedicalDateError) as cm:
            DxDate(cleaned_data)
        self.assertIn("Date conflict", str(cm.exception))

        cleaned_data = {
            "report_datetime": get_utcnow(),
            "dx_date": get_utcnow().date() - relativedelta(years=3),
            "dx_ago": "1y",
        }
        with self.assertRaises(MedicalDateError) as cm:
            DxDate(cleaned_data)
        self.assertIn("Date conflict", str(cm.exception))

    def test_rx_date(self):
        cleaned_data = {
            "report_datetime": get_utcnow(),
            "dx_ago": "3y",
        }
        dx_date = DxDate(cleaned_data)
        cleaned_data = {
            "report_datetime": get_utcnow(),
            "dx_date": get_utcnow().date() - relativedelta(years=3),
        }
        with self.assertRaises(MedicalDateError) as cm:
            RxDate(cleaned_data, reference_date=dx_date)
        self.assertIn("Complete the treatment date", str(cm.exception))

        cleaned_data = {
            "report_datetime": get_utcnow(),
            "dx_date": get_utcnow().date() - relativedelta(years=3),
            "rx_init_date": get_utcnow().date()
            - relativedelta(years=3)
            - relativedelta(days=1),
        }
        with self.assertRaises(MedicalDateError) as cm:
            RxDate(cleaned_data, reference_date=dx_date)
        self.assertIn("date must be on or after", str(cm.exception))

        cleaned_data = {
            "report_datetime": get_utcnow(),
            "dx_date": get_utcnow().date() - relativedelta(years=3),
            "rx_init_date": get_utcnow().date()
            - relativedelta(years=3)
            + relativedelta(days=1),
        }
        try:
            RxDate(cleaned_data, reference_date=dx_date)
        except MedicalDateError as e:
            self.fail(f"Exception unexpectedly raised. Got {e}")
