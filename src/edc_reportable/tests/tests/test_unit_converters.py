from django.test import TestCase, tag
from edc_utils import round_half_away_from_zero as rnd

from edc_reportable.units import (
    GRAMS_PER_LITER,
    MICROMOLES_PER_LITER,
    MILLIGRAMS_PER_DECILITER,
    MILLIMOLES_PER_LITER,
)
from edc_reportable.utils import convert_units


class TestParser(TestCase):

    @tag("68")
    def test_convert_tbil1(self):
        converted_value = convert_units(
            label="tbil",
            value=0.00292,
            units_from=GRAMS_PER_LITER,
            units_to=MILLIMOLES_PER_LITER,
        )
        self.assertEqual(converted_value, 0.005)

    def test_convert_tbil4(self):
        converted_value = convert_units(
            label="tbil",
            value=0.00292,
            units_from=GRAMS_PER_LITER,
            units_to=MICROMOLES_PER_LITER,
        )
        self.assertEqual(rnd(converted_value, 4), 4.9949)

    @tag("68")
    def test_convert_tbil2(self):
        converted_value = convert_units(
            label="tbil",
            value=5.0,
            units_from=MICROMOLES_PER_LITER,
            units_to=MILLIMOLES_PER_LITER,
        )
        self.assertEqual(rnd(converted_value, 3), 0.005)

    @tag("68")
    def test_convert_tbil3(self):
        converted_value = convert_units(
            label="tbil",
            value=5.0,
            units_from=GRAMS_PER_LITER,
            units_to=MILLIGRAMS_PER_DECILITER,
        )
        self.assertEqual(rnd(converted_value, 1), 500.0)

    @tag("68")
    def test_convert_glucose(self):
        """mg/dL to mmol/L"""

        values = [
            (1.0, 0.056),
            (19.0, 1.055),
            (33.0, 1.832),
            (37.0, 2.054),
            (125.0, 6.938),
        ]

        for value, expected_value in values:
            converted_value = convert_units(
                label="glucose",
                value=value,
                units_from=MILLIGRAMS_PER_DECILITER,
                units_to=MILLIMOLES_PER_LITER,
            )
            self.assertEqual(rnd(converted_value, 3), expected_value)

        converted_value = convert_units(
            label="glucose",
            value=558.559,
            units_from=MILLIMOLES_PER_LITER,
            units_to=MILLIMOLES_PER_LITER,
        )
        self.assertEqual(558.559, converted_value)

        converted_value = convert_units(
            label="glucose",
            value=6.9375,
            units_from=MILLIMOLES_PER_LITER,
            units_to=MILLIMOLES_PER_LITER,
        )
        self.assertEqual(6.9375, converted_value)

    @tag("68")
    def test_convert_creatinine(self):
        """mg/dL to umol/L"""

        values = [
            (1.0, 0.0113),
            (19.0, 0.2149),
            (33.0, 0.3733),
            (37.0, 0.4186),
            (50.0, 0.5656),
        ]

        for value, converted_value in values:
            converted_value = convert_units(
                label="creatinine",
                value=value,
                units_from=MILLIGRAMS_PER_DECILITER,
                units_to=MICROMOLES_PER_LITER,
            )
            self.assertEqual(converted_value, converted_value)

        converted_value = convert_units(
            label="creatinine",
            value=0.2149,
            units_from=MICROMOLES_PER_LITER,
            units_to=MICROMOLES_PER_LITER,
        )
        self.assertEqual(0.2149, converted_value)
