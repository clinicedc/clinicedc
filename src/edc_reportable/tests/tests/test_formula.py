from django.test import TestCase
from edc_constants.constants import MALE

from edc_reportable import MILLIMOLES_PER_LITER
from edc_reportable.formula import Formula, FormulaError, clean_and_validate_phrase


class TestParser(TestCase):

    def test1(self):
        f = Formula("7<x<8")
        self.assertEqual(f.lower, 7)
        self.assertFalse(f.lower_inclusive)
        self.assertEqual(f.upper, 8)
        self.assertFalse(f.upper_inclusive)

    def test2(self):
        f = Formula("7<=x<8")
        self.assertEqual(f.lower, 7)
        self.assertTrue(f.lower_inclusive)
        self.assertEqual(f.upper, 8)
        self.assertFalse(f.upper_inclusive)

    def test3(self):
        f = Formula("7<x<=8")
        self.assertEqual(f.lower, 7)
        self.assertFalse(f.lower_inclusive)
        self.assertEqual(f.upper, 8)
        self.assertTrue(f.upper_inclusive)

    def test4(self):
        f = Formula("7<=x<=8")
        self.assertEqual(f.lower, 7)
        self.assertTrue(f.lower_inclusive)
        self.assertEqual(f.upper, 8)
        self.assertTrue(f.upper_inclusive)

    def test5(self):
        f = Formula(".7<=x<=.8")
        self.assertEqual(f.lower, 0.7)
        self.assertTrue(f.lower_inclusive)
        self.assertEqual(f.upper, 0.8)
        self.assertTrue(f.upper_inclusive)

    def test6(self):
        f = Formula("0.77<=x<=0.88")
        self.assertEqual(f.lower, 0.77)
        self.assertTrue(f.lower_inclusive)
        self.assertEqual(f.upper, 0.88)
        self.assertTrue(f.upper_inclusive)

    def test7(self):
        f = Formula("0.77 <= x <= 0.88")
        self.assertEqual(f.lower, 0.77)
        self.assertTrue(f.lower_inclusive)
        self.assertEqual(f.upper, 0.88)
        self.assertTrue(f.upper_inclusive)

    def test8(self):
        f = Formula("x <= 0.88")
        self.assertIsNone(f.lower)
        self.assertFalse(f.lower_inclusive)
        self.assertEqual(f.upper, 0.88)
        self.assertTrue(f.upper_inclusive)

    def test9(self):
        f = Formula("0.77 <= x")
        self.assertEqual(f.lower, 0.77)
        self.assertTrue(f.lower_inclusive)
        self.assertIsNone(f.upper)
        self.assertFalse(f.upper_inclusive)

    def test10(self):
        self.assertEqual(
            Formula("0.77 <= x <= 0.88", units=MILLIMOLES_PER_LITER).description,
            f"0.77<=x<=0.88 {MILLIMOLES_PER_LITER}",
        )
        self.assertEqual(
            Formula("0.77 <= x <= 0.88", units=MILLIMOLES_PER_LITER, gender=MALE).description,
            f"0.77<=x<=0.88 {MILLIMOLES_PER_LITER} {MALE}",
        )

    def test11(self):
        self.assertRaises(FormulaError, clean_and_validate_phrase, "0.77 <= x = 0.88")
        self.assertRaises(FormulaError, clean_and_validate_phrase, "0.77 <= x =")

        self.assertRaises(FormulaError, clean_and_validate_phrase, "<0.77")

        self.assertRaises(FormulaError, clean_and_validate_phrase, "<77")

        self.assertRaises(FormulaError, clean_and_validate_phrase, "=77")

        self.assertRaises(FormulaError, clean_and_validate_phrase, ">77")

        self.assertRaises(FormulaError, clean_and_validate_phrase, "0.77 >= x > 0.88")

        self.assertRaises(FormulaError, clean_and_validate_phrase, "0.77 =< x < 0.88")

        self.assertRaises(
            FormulaError, clean_and_validate_phrase, "0.77 < x < 0.88 < x < 0.88"
        )
