from django.test import TestCase, tag
from edc_constants.constants import MALE

from edc_reportable.formula import (
    Formula,
    FormulaError,
    clean_and_validate_phrase,
    formula,
)


class TestParser(TestCase):
    @tag("1")
    def test1(self):
        formula = Formula("7<x<8")
        self.assertEqual(formula.lower, 7)
        self.assertFalse(formula.lower_inclusive)
        self.assertEqual(formula.upper, 8)
        self.assertFalse(formula.upper_inclusive)

    @tag("1")
    def test2(self):
        formula = Formula("7<=x<8")
        self.assertEqual(formula.lower, 7)
        self.assertTrue(formula.lower_inclusive)
        self.assertEqual(formula.upper, 8)
        self.assertFalse(formula.upper_inclusive)

    @tag("1")
    def test3(self):
        formula = Formula("7<x<=8")
        self.assertEqual(formula.lower, 7)
        self.assertFalse(formula.lower_inclusive)
        self.assertEqual(formula.upper, 8)
        self.assertTrue(formula.upper_inclusive)

    @tag("1")
    def test4(self):
        formula = Formula("7<=x<=8")
        self.assertEqual(formula.lower, 7)
        self.assertTrue(formula.lower_inclusive)
        self.assertEqual(formula.upper, 8)
        self.assertTrue(formula.upper_inclusive)

    @tag("1")
    def test5(self):
        formula = Formula(".7<=x<=.8")
        self.assertEqual(formula.lower, 0.7)
        self.assertTrue(formula.lower_inclusive)
        self.assertEqual(formula.upper, 0.8)
        self.assertTrue(formula.upper_inclusive)

    @tag("1")
    def test6(self):
        formula = Formula("0.77<=x<=0.88")
        self.assertEqual(formula.lower, 0.77)
        self.assertTrue(formula.lower_inclusive)
        self.assertEqual(formula.upper, 0.88)
        self.assertTrue(formula.upper_inclusive)

    @tag("1")
    def test7(self):
        formula = Formula("0.77 <= x <= 0.88")
        self.assertEqual(formula.lower, 0.77)
        self.assertTrue(formula.lower_inclusive)
        self.assertEqual(formula.upper, 0.88)
        self.assertTrue(formula.upper_inclusive)

    @tag("1")
    def test8(self):
        formula = Formula("x <= 0.88")
        self.assertIsNone(formula.lower)
        self.assertFalse(formula.lower_inclusive)
        self.assertEqual(formula.upper, 0.88)
        self.assertTrue(formula.upper_inclusive)

    @tag("1")
    def test9(self):
        formula = Formula("0.77 <= x")
        self.assertEqual(formula.lower, 0.77)
        self.assertTrue(formula.lower_inclusive)
        self.assertIsNone(formula.upper)
        self.assertFalse(formula.upper_inclusive)

    @tag("1")
    def test10(self):
        self.assertEqual(formula("0.77 <= x <= 0.88"), "0.77<=x<=0.88")
        self.assertEqual(formula("0.77 <= x <= 0.88", gender=MALE), "0.77<=x<=0.88 M")

    @tag("1")
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
