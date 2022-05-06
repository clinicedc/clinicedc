from django.test import TestCase

from edc_reportable import convert_units
from edc_reportable.units import (
    MICROMOLES_PER_LITER,
    MILLIGRAMS_PER_DECILITER,
    MILLIMOLES_PER_LITER,
)


class TestParser(TestCase):
    def test_convert_glucose(self):
        """mg/dL to mmol/L"""

        values = [
            (1.0, 18.0180),
            (19.0, 342.3423),
            (33.0, 594.5946),
            (37.0, 666.6667),
            (125.0, 6.9375),
        ]

        for value, converted_value in values:
            converted_value = convert_units(
                value,
                units_from=MILLIGRAMS_PER_DECILITER,
                units_to=MILLIMOLES_PER_LITER,
            )
            self.assertEqual(converted_value, converted_value)

        converted_value = convert_units(
            558.558559, units_from=MILLIMOLES_PER_LITER, units_to=MILLIMOLES_PER_LITER
        )
        self.assertEqual(558.5586, converted_value)

        converted_value = convert_units(
            6.9375, units_from=MILLIMOLES_PER_LITER, units_to=MILLIMOLES_PER_LITER
        )
        self.assertEqual(6.9375, converted_value)

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
                value,
                units_from=MILLIGRAMS_PER_DECILITER,
                units_to=MICROMOLES_PER_LITER,
            )
            self.assertEqual(converted_value, converted_value)

        converted_value = convert_units(
            0.2149, units_from=MICROMOLES_PER_LITER, units_to=MICROMOLES_PER_LITER
        )
        self.assertEqual(0.2149, converted_value)
