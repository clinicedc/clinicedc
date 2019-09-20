from django.test import TestCase, tag
from edc_constants.constants import MALE
from edc_reportable import parse, unparse, ParserError


class TestParser(TestCase):
    def test1(self):
        p = parse("7<x<8")
        self.assertEqual(p.lower, 7)
        self.assertFalse(p.lower_inclusive)
        self.assertEqual(p.upper, 8)
        self.assertFalse(p.upper_inclusive)

    def test2(self):
        p = parse("7<=x<8")
        self.assertEqual(p.lower, 7)
        self.assertTrue(p.lower_inclusive)
        self.assertEqual(p.upper, 8)
        self.assertFalse(p.upper_inclusive)

    def test3(self):
        p = parse("7<x<=8")
        self.assertEqual(p.lower, 7)
        self.assertFalse(p.lower_inclusive)
        self.assertEqual(p.upper, 8)
        self.assertTrue(p.upper_inclusive)

    def test4(self):
        p = parse("7<=x<=8")
        self.assertEqual(p.lower, 7)
        self.assertTrue(p.lower_inclusive)
        self.assertEqual(p.upper, 8)
        self.assertTrue(p.upper_inclusive)

    def test5(self):
        p = parse(".7<=x<=.8")
        self.assertEqual(p.lower, 0.7)
        self.assertTrue(p.lower_inclusive)
        self.assertEqual(p.upper, 0.8)
        self.assertTrue(p.upper_inclusive)

    def test6(self):
        p = parse("0.77<=x<=0.88")
        self.assertEqual(p.lower, 0.77)
        self.assertTrue(p.lower_inclusive)
        self.assertEqual(p.upper, 0.88)
        self.assertTrue(p.upper_inclusive)

    def test7(self):
        p = parse("0.77 <= x <= 0.88")
        self.assertEqual(p.lower, 0.77)
        self.assertTrue(p.lower_inclusive)
        self.assertEqual(p.upper, 0.88)
        self.assertTrue(p.upper_inclusive)

    def test8(self):
        p = parse("x <= 0.88")
        self.assertIsNone(p.lower)
        self.assertIsNone(p.lower_inclusive)
        self.assertEqual(p.upper, 0.88)
        self.assertTrue(p.upper_inclusive)

    def test9(self):
        p = parse("0.77 <= x")
        self.assertEqual(p.lower, 0.77)
        self.assertTrue(p.lower_inclusive)
        self.assertIsNone(p.upper)
        self.assertIsNone(p.upper_inclusive)

    def test10(self):
        p = parse("0.77 <= x <= 0.88")
        self.assertEqual(unparse(**p), "0.77<=x<=0.88")
        p = parse("0.77 <= x <= 0.88")
        self.assertEqual(unparse(gender=MALE, **p), "0.77<=x<=0.88 M")

    def test11(self):
        self.assertRaises(ParserError, parse, "0.77 <= x = 0.88")
        self.assertRaises(ParserError, parse, "0.77 <= x =")

        self.assertRaises(ParserError, parse, "<0.77")

        self.assertRaises(ParserError, parse, "<77")

        self.assertRaises(ParserError, parse, "=77")

        self.assertRaises(ParserError, parse, ">77")

        self.assertRaises(ParserError, parse, "0.77 >= x > 0.88")

        self.assertRaises(ParserError, parse, "0.77 =< x < 0.88")

        self.assertRaises(ParserError, parse, "0.77 < x < 0.88 < x < 0.88")
