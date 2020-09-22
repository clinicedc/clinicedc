from django.test import TestCase

from ..checkdigit_mixins import LuhnMixin, LuhnOrdMixin
from ..identifier import Identifier


class TestIdentifier(TestCase):
    def test_valid_checkdigit(self):
        mixin = LuhnMixin()
        checkdigit = mixin.calculate_checkdigit("98765")
        self.assertEqual(checkdigit, "1")
        checkdigit = mixin.calculate_checkdigit("98766")
        self.assertEqual(checkdigit, "9")
        checkdigit = mixin.calculate_checkdigit("98767")
        self.assertEqual(checkdigit, "7")

    def test_luhn_ord_mixin(self):
        mixin = LuhnOrdMixin()
        self.assertEqual("4", mixin.calculate_checkdigit("ABCDE"))
        self.assertEqual("8", mixin.calculate_checkdigit("ABCDEF"))
        self.assertEqual("0", mixin.calculate_checkdigit("ABCDEFG"))

    def test_identifier(self):
        instance = Identifier()
        self.assertEqual("1", instance.identifier)
        instance = Identifier()
        self.assertEqual("2", instance.identifier)
