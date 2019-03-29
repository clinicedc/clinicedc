from django.test import TestCase, tag

from edc_lab.lab import (
    AliquotType,
    AliquotTypeNumericCodeError,
    AliquotTypeAlphaCodeError,
)


class TestAliquotType(TestCase):
    def setUp(self):
        self.wb = AliquotType(name="whole_blood", numeric_code="02", alpha_code="WB")
        self.bc = AliquotType(name="buffy_coat", numeric_code="12", alpha_code="BC")

    def test_bad_aliquot_type1(self):
        self.assertRaises(
            AliquotTypeNumericCodeError,
            AliquotType,
            name="whole_blood",
            numeric_code="AA",
            alpha_code="WB",
        )

    def test_bad_aliquot_type2(self):
        self.assertRaises(
            AliquotTypeAlphaCodeError,
            AliquotType,
            name="whole_blood",
            numeric_code="02",
            alpha_code="99",
        )

    def test_aliquot_type_repr(self):
        aliquot_type = AliquotType(name="aliquot", numeric_code="00", alpha_code="AA")
        self.assertTrue(repr(aliquot_type))

    def test_aliquot_type_derivatives_single(self):
        """Asserts can add a derivative.
        """
        self.wb.add_derivatives(self.bc)
        self.assertEqual(self.wb.derivatives, [self.bc])

    def test_aliquot_type_derivatives_multi(self):
        """Asserts can add more than one derivative.
        """
        pl = AliquotType(name="plasma", numeric_code="32", alpha_code="PL")
        self.wb.add_derivatives(self.bc, pl)
        self.assertEqual(self.wb.derivatives, [self.bc, pl])
