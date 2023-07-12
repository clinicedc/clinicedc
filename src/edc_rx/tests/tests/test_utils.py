from django.forms import Form
from django.test import TestCase

from edc_rx.utils import TotalDaysMismatch, validate_total_days


class TestRxUtils(TestCase):
    def test_validate_total_days_mismatch_raises(self):
        form = Form()
        for invalid_combo in [
            (0, 0, 0),
            (None, None, None),
            (1, 1, 1),
            (20, 10, 1),
            (1, 20, 0),
            (1, 20, None),
            (30, 30, 30),
            (31, 0, 0),
            (31, None, None),
        ]:
            clinic_days = invalid_combo[0]
            club_days = invalid_combo[1]
            purchased_days = invalid_combo[2]
            with self.subTest(
                clinic_days=clinic_days,
                club_days=club_days,
                purchased_days=purchased_days,
            ):
                form.cleaned_data = {
                    "rx_days": 30,
                    "clinic_days": clinic_days,
                    "club_days": club_days,
                    "purchased_days": purchased_days,
                }
                with self.assertRaises(TotalDaysMismatch):
                    validate_total_days(form=form)

    def test_validate_total_days_match_ok(self):
        form = Form()
        for valid_combo in [
            (30, 0, 0),
            (0, 30, 0),
            (0, 0, 30),
            (30, 0, None),
            (30, None, None),
            (20, 10, 0),
            (20, 10, None),
            (0, 10, 20),
            (None, 10, 20),
            (10, 10, 10),
            (5, 20, 5),
        ]:
            clinic_days = valid_combo[0]
            club_days = valid_combo[1]
            purchased_days = valid_combo[2]
            with self.subTest(
                clinic_days=clinic_days,
                club_days=club_days,
                purchased_days=purchased_days,
            ):
                form.cleaned_data = {
                    "rx_days": 30,
                    "clinic_days": clinic_days,
                    "club_days": club_days,
                    "purchased_days": purchased_days,
                }
                try:
                    validate_total_days(form=form)
                except TotalDaysMismatch as e:
                    self.fail(f"TotalDaysMismatch unexpectedly raised. Got {e}")

    def test_validate_total_days_0_with_mismatch_raises(self):
        form = Form()
        for invalid_combo in [
            (1, 1, 1),
            (20, 10, 1),
            (1, 20, 0),
            (1, 20, None),
            (30, 30, 30),
            (31, 0, 0),
            (31, None, None),
        ]:
            clinic_days = invalid_combo[0]
            club_days = invalid_combo[1]
            purchased_days = invalid_combo[2]
            with self.subTest(
                clinic_days=clinic_days,
                club_days=club_days,
                purchased_days=purchased_days,
            ):
                form.cleaned_data = {
                    "rx_days": 0,
                    "clinic_days": clinic_days,
                    "club_days": club_days,
                    "purchased_days": purchased_days,
                }
                with self.assertRaises(TotalDaysMismatch):
                    validate_total_days(form=form)

    def test_validate_total_days_0_with_match_ok(self):
        form = Form()
        for valid_combo in [
            (0, 0, 0),
            (None, None, None),
            (0, None, 0),
            (None, 0, None),
        ]:
            clinic_days = valid_combo[0]
            club_days = valid_combo[1]
            purchased_days = valid_combo[2]
            with self.subTest(
                clinic_days=clinic_days,
                club_days=club_days,
                purchased_days=purchased_days,
            ):
                form.cleaned_data = {
                    "rx_days": 0,
                    "clinic_days": clinic_days,
                    "club_days": club_days,
                    "purchased_days": purchased_days,
                }
                try:
                    validate_total_days(form=form)
                except TotalDaysMismatch as e:
                    self.fail(f"TotalDaysMismatch unexpectedly raised. Got {e}")
