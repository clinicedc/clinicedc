from django.db.models import NOT_PROVIDED
from django.test import TestCase
from edc_reportable import MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER_DISPLAY

from edc_lab_panel.model_mixin_factory import field_attrs


class TestFieldAttrs(TestCase):
    def test_decimal_places_not_specified_defaults_to_2(self):
        field_classes = field_attrs.get_field_attrs_for_utestid(
            utest_id="sodium",
            units_choices=(MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER_DISPLAY),
        )
        self.assertEqual(field_classes["sodium_value"].decimal_places, 2)

    def test_decimal_places_provided(self):
        for specified_dp in [1, 2, 3, 4, 5]:
            with self.subTest(decimal_places=specified_dp):
                field_classes = field_attrs.get_field_attrs_for_utestid(
                    utest_id="sodium",
                    units_choices=(MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER_DISPLAY),
                    decimal_places=specified_dp,
                )
                self.assertEqual(field_classes["sodium_value"].decimal_places, specified_dp)

    def test_0_decimal_places(self):
        field_classes = field_attrs.get_field_attrs_for_utestid(
            utest_id="sodium",
            units_choices=(MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER_DISPLAY),
            decimal_places=0,
        )
        self.assertEqual(field_classes["sodium_value"].decimal_places, 0)

    def test_max_digits_not_specified_defaults_to_8(self):
        field_classes = field_attrs.get_field_attrs_for_utestid(
            utest_id="sodium",
            units_choices=(MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER_DISPLAY),
        )
        self.assertEqual(field_classes["sodium_value"].max_digits, 8)

    def test_max_digits_provided(self):
        for specified_md in [1, 2, 3, 4, 5, 8, 10]:
            with self.subTest(max_digits=specified_md):
                field_classes = field_attrs.get_field_attrs_for_utestid(
                    utest_id="sodium",
                    units_choices=(MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER_DISPLAY),
                    max_digits=specified_md,
                )
                self.assertEqual(field_classes["sodium_value"].max_digits, specified_md)

    def test_0_max_digits_sets_to_0(self):
        """`max_digits` should never be zero (Django enforces this).

        This test asserts that `get_field_attrs_for_utestid()` doesn't
        silently convert an invalid `max_digits` zero value to the
        default (of 8 decimal places).
        """
        field_classes = field_attrs.get_field_attrs_for_utestid(
            utest_id="sodium",
            units_choices=(MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER_DISPLAY),
            max_digits=0,
        )
        self.assertEqual(field_classes["sodium_value"].max_digits, 0)

    def test_help_text(self):
        field_classes = field_attrs.get_field_attrs_for_utestid(
            utest_id="sodium",
            units_choices=(MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER_DISPLAY),
        )
        self.assertEqual(field_classes["sodium_value"].help_text, "")

        field_classes = field_attrs.get_field_attrs_for_utestid(
            utest_id="sodium",
            units_choices=(MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER_DISPLAY),
            help_text="some help text...",
        )
        self.assertEqual(field_classes["sodium_value"].help_text, "some help text...")

    def test_default_units(self):
        field_classes = field_attrs.get_field_attrs_for_utestid(
            utest_id="sodium",
            units_choices=(MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER_DISPLAY),
        )
        self.assertEqual(field_classes["sodium_units"].default, NOT_PROVIDED)

        field_classes = field_attrs.get_field_attrs_for_utestid(
            utest_id="sodium",
            units_choices=(MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER_DISPLAY),
            default_units=MILLIMOLES_PER_LITER,
        )
        self.assertEqual(field_classes["sodium_units"].default, MILLIMOLES_PER_LITER)
