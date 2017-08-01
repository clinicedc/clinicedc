from django.test import TestCase, tag

from ..checkdigit_mixins import LuhnMixin, LuhnOrdMixin
from ..identifier import Identifier


@tag('identifier')
class TestIdentifier(TestCase):

    def test_valid_checkdigit(self):
        mixin = LuhnMixin()
        checkdigit = mixin.calculate_checkdigit('98765')
        self.assertTrue(mixin.is_valid_checkdigit('98765', checkdigit))
        checkdigit = mixin.calculate_checkdigit('98766')
        self.assertTrue(mixin.is_valid_checkdigit('98766', checkdigit))
        checkdigit = mixin.calculate_checkdigit('98767')
        self.assertTrue(mixin.is_valid_checkdigit('98767', checkdigit))

    def test_luhn_mixin(self):
        mixin = LuhnMixin()
        self.assertEqual('1', mixin.calculate_checkdigit('98765'))
        self.assertEqual('9', mixin.calculate_checkdigit('98766'))
        self.assertEqual('7', mixin.calculate_checkdigit('98767'))

    def test_luhn_ord_mixin(self):
        mixin = LuhnOrdMixin()
        self.assertEqual('4', mixin.calculate_checkdigit('ABCDE'))
        self.assertEqual('8', mixin.calculate_checkdigit('ABCDEF'))
        self.assertEqual('0', mixin.calculate_checkdigit('ABCDEFG'))

    def test_identifier(self):
        instance = Identifier()
        self.assertEqual('1', instance.identifier)
        instance = Identifier()
        self.assertEqual('2', instance.identifier)
