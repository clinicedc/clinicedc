from django.test.testcases import TestCase

from .alphanumeric_identifier import AlphanumericIdentifier
from .checkdigit_mixins import LuhnMixin, LuhnOrdMixin
from .exceptions import IdentifierError, CheckDigitError
from .identifier import Identifier
from .identifier_with_checkdigit import IdentifierWithCheckdigit
from .models import IdentifierHistory
from .numeric_identifier import NumericIdentifier, NumericIdentifierWithModulus
from .short_identifier import ShortIdentifier


class TestIdentifierError(Exception):
    pass


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

    def test_identifier_with_checkdigit(self):
        instance = IdentifierWithCheckdigit()
        self.assertEqual('18', instance.identifier)
        instance = IdentifierWithCheckdigit()
        self.assertEqual('26', instance.identifier)
        instance = IdentifierWithCheckdigit()
        self.assertEqual('34', instance.identifier)

    def test_short_identifier(self):
        ShortIdentifier.prefix_pattern = '^[0-9]{2}$'
        short_identifier = ShortIdentifier(options=dict(prefix=22))
        expected_identifier = '{}{}'.format('22', short_identifier.options.get('random_string'))
        self.assertEqual(short_identifier.identifier, expected_identifier)
        self.assertIsInstance(
            IdentifierHistory.objects.get(identifier=expected_identifier),
            IdentifierHistory
        )
        self.assertIsInstance(
            IdentifierHistory.objects.get(identifier=short_identifier.identifier),
            IdentifierHistory
        )
        self.assertIsNotNone(short_identifier.identifier)
        ShortIdentifier.prefix_pattern = None

    def test_short_identifier_with_last(self):
        ShortIdentifier.prefix_pattern = '^[0-9]{2}$'
        ShortIdentifier.checkdigit_pattern = None
        ShortIdentifier.history_model.objects.create(
            identifier='22KVTB4',
            identifier_type=ShortIdentifier.name,
            identifier_prefix='22')
        short_identifier = ShortIdentifier(options={'prefix': 22})
        expected_identifier = '{}{}'.format('22', short_identifier.options.get('random_string'))
        self.assertEqual(short_identifier.identifier, expected_identifier)
        self.assertNotEqual(short_identifier.identifier, '22KVTB4')
        self.assertIsInstance(
            IdentifierHistory.objects.get(identifier=expected_identifier),
            IdentifierHistory
        )
        self.assertIsInstance(
            IdentifierHistory.objects.get(identifier=short_identifier.identifier),
            IdentifierHistory
        )
        self.assertIsNotNone(short_identifier.identifier)
        ShortIdentifier.prefix_pattern = None

    def test_short_identifier_catches_duplicate_limit(self):
        ntries = 0
        ShortIdentifier.identifier_pattern = '^\w+$'
        ShortIdentifier.allowed_chars = 'AB'
        instance = ShortIdentifier()
        min_tries = instance.duplicate_tries
        max_tries = min_tries + 10
        assert_msg = None
        while ntries <= max_tries:
            ntries += 1
            try:
                instance = ShortIdentifier()
            except IdentifierError as e:
                assert_msg = (
                    'No available identifiers on {}th attempt. Limit is {}. Got {}'.format(
                        ntries, min_tries, str(e)))
                break
        self.assertTrue(ntries <= min_tries, assert_msg)

    def test_numeric_basic(self):
        NumericIdentifier.identifier_pattern = r'^[0-9]{8}$'
        NumericIdentifier.seed = ('10000000')
        numeric_identifier = NumericIdentifier(None)
        self.assertEqual(numeric_identifier.identifier, '100000017')
        numeric_identifier.next_identifier()
        self.assertEqual(numeric_identifier.identifier, '100000025')
        numeric_identifier.next_identifier()
        self.assertEqual(numeric_identifier.identifier, '100000033')
        numeric_identifier.next_identifier()
        self.assertEqual(numeric_identifier.identifier, '100000041')

    def test_numeric_without_checkdigit(self):
        NumericIdentifier.identifier_pattern = r'^[0-9]{8}$'
        NumericIdentifier.seed = ('10000000')
        NumericIdentifier.checkdigit_pattern = None
        numeric_identifier = NumericIdentifier(None)
        self.assertEqual(numeric_identifier.identifier, '10000001')
        numeric_identifier.next_identifier()
        self.assertEqual(numeric_identifier.identifier, '10000002')
        numeric_identifier.next_identifier()
        self.assertEqual(numeric_identifier.identifier, '10000003')
        numeric_identifier.next_identifier()
        self.assertEqual(numeric_identifier.identifier, '10000004')

    def test_numeric_without_checkdigit_last(self):
        NumericIdentifier.identifier_pattern = r'^[0-9]{8}$'
        NumericIdentifier.seed = ('10000000')
        NumericIdentifier.checkdigit_pattern = None
        numeric_identifier = NumericIdentifier(last_identifier='10000004')
        self.assertEqual(numeric_identifier.identifier, '10000005')

    def test_numeric_without_checkdigit_history(self):
        NumericIdentifier.identifier_pattern = r'^[0-9]{8}$'
        NumericIdentifier.seed = ('10000000')
        NumericIdentifier.checkdigit_pattern = None
        numeric_identifier = NumericIdentifier(None)
        self.assertEqual(numeric_identifier.identifier, '10000001')
        numeric_identifier.next_identifier()
        self.assertEqual(numeric_identifier.identifier, '10000002')
        numeric_identifier.next_identifier()
        self.assertEqual(numeric_identifier.identifier, '10000003')
        numeric_identifier.next_identifier()
        self.assertEqual(numeric_identifier.identifier, '10000004')
        numeric_identifier = NumericIdentifier()
        self.assertEqual(numeric_identifier.identifier, '10000005')

    def test_numeric_pattern(self):
        NumericIdentifier.identifier_pattern = r'^[0-9]{10}\-[0-9]{1}$'
        NumericIdentifier.seed = ('1000000008')
        self.assertRaises(IdentifierError, NumericIdentifier, None)

    def test_numeric_seed(self):
        NumericIdentifier.separator = None
        NumericIdentifier.identifier_pattern = r'^[0-9]{10}$'
        NumericIdentifier.seed = ('1999999996')
        instance = NumericIdentifier(None)
        self.assertEqual(instance.identifier, '19999999972')
        instance.next_identifier()
        self.assertEqual(instance.identifier, '19999999980')
        instance.next_identifier()
        self.assertEqual(instance.identifier, '19999999998')
        instance.next_identifier()
        self.assertEqual(instance.identifier, '20000000008')

    def test_numeric_with_last(self):
        NumericIdentifier.separator = None
        NumericIdentifier.identifier_pattern = r'^[0-9]{9}$'
        NumericIdentifier.checkdigit_pattern = r'^[0-9]{1}$'
        NumericIdentifier.seed = ('100000008')
        instance = NumericIdentifier(last_identifier='1999999996')
        self.assertEqual(instance.identifier, '2000000006')

    def test_numeric_separator(self):
        NumericIdentifier.separator = '-'
        NumericIdentifier.identifier_pattern = r'^[0-9]{4}\-[0-9]{4}$'
        NumericIdentifier.checkdigit_pattern = r'^\-[0-9]{1}$'
        NumericIdentifier.seed = '1000-0000'
        numeric_identifier = NumericIdentifier(None)
        self.assertEqual(numeric_identifier.identifier, '1000-0001-7')

    def test_numeric_modulus(self):
        NumericIdentifierWithModulus.separator = '-'
        NumericIdentifierWithModulus.identifier_pattern = r'^[0-9]{4}[0-9]{4}[0-9]{2}$'
        NumericIdentifierWithModulus.checkdigit_pattern = r'^\-[0-9]{2}$'
        NumericIdentifierWithModulus.seed = '1000000010'
        numeric_identifier = NumericIdentifierWithModulus(None)
        self.assertEqual(numeric_identifier.identifier, '1000000011-10')
        self.assertEqual(next(numeric_identifier), '1000000012-11')

    def test_numeric_modulus_with_separator(self):
        NumericIdentifierWithModulus.separator = '-'
        NumericIdentifierWithModulus.identifier_pattern = r'^[0-9]{4}\-[0-9]{4}$'
        NumericIdentifierWithModulus.checkdigit_pattern = r'^\-[0-9]{2}$'
        NumericIdentifierWithModulus.seed = '1000-0000'
        numeric_identifier = NumericIdentifierWithModulus(None)
        self.assertEqual(numeric_identifier.identifier, '1000-0001-11')
        self.assertEqual(next(numeric_identifier), '1000-0002-12')

    def test_split_checkdigit_one(self):
        """Asserts can split identifier with checkdigit into identifier, checkdigit."""
        class DummyIdentifierWithCheckdigit(IdentifierWithCheckdigit):
            def calculate_checkdigit(self, identifier):
                return '1'

        identifier_with_checkdigit = '987651'
        instance = IdentifierWithCheckdigit()
        identifier = instance.remove_checkdigit(identifier_with_checkdigit)
        checkdigit = identifier_with_checkdigit.replace(identifier, '')
        self.assertEqual(identifier, identifier_with_checkdigit[:-1])
        self.assertEqual(checkdigit, identifier_with_checkdigit[-1:])

    def test_split_checkdigit_two(self):
        """Asserts can split identifier with checkdigit into identifier, checkdigit.

        Tries with a different the checkdigit_pattern"""
        class DummyIdentifierWithCheckdigit(IdentifierWithCheckdigit):
            checkdigit_pattern = r'^[0-9]{2}$'

            def calculate_checkdigit(self, identifier):
                return '51'

        instance = DummyIdentifierWithCheckdigit()
        identifier_with_checkdigit = '987651'
        identifier = instance.remove_checkdigit(identifier_with_checkdigit)
        checkdigit = identifier_with_checkdigit.replace(identifier, '')
        self.assertEqual(identifier, identifier_with_checkdigit[:-2])
        self.assertEqual(checkdigit, identifier_with_checkdigit[-2:])

    def test_split_checkdigit_exception(self):
        """Asserts raises an exception if cannot split based on the pattern and identifier.

        Note, checkdigit_pattern does not match"""
        class DummyIdentifierWithCheckDigit(IdentifierWithCheckdigit):

            checkdigit_pattern = r'^[0-9]{2}$'

            def calculate_checkdigit(self, identifier):
                return '54'

        instance = DummyIdentifierWithCheckDigit()
        identifier_with_checkdigit = '98765-4'
        self.assertRaises(CheckDigitError, instance.remove_checkdigit, identifier_with_checkdigit)

    def test_checkdigit(self):
        identifier = 'AAA00007'
        alpha_identifier = AlphanumericIdentifier(identifier)
        identifier_with_checkdigit = alpha_identifier.identifier
        identifier = alpha_identifier.remove_checkdigit(identifier_with_checkdigit)
        checkdigit = identifier_with_checkdigit.replace(identifier, '')
        self.assertEqual(checkdigit, '5')
        self.assertEqual(identifier_with_checkdigit, 'AAA00015')
        alpha_identifier.next()
        self.assertEqual(alpha_identifier.identifier, 'AAA00023')
        alpha_identifier.next()
        self.assertEqual(alpha_identifier.identifier, 'AAA00031')

    def test_alphanumeric(self):
        AlphanumericIdentifier.alpha_pattern = r'^[A-Z]{3}$'
        AlphanumericIdentifier.numeric_pattern = r'^[0-9]{4}$'
        AlphanumericIdentifier.seed = ['AAA', '0000']
        alpha_id = AlphanumericIdentifier(None)
        self.assertEqual(alpha_id.identifier, 'AAA00015')
        self.assertEqual(next(alpha_id), 'AAA00023')
        self.assertEqual(next(alpha_id), 'AAA00031')
        self.assertEqual(next(alpha_id), 'AAA00049')
        self.assertEqual(next(alpha_id), 'AAA00057')
        self.assertEqual(next(alpha_id), 'AAA00065')

    def test_alphanumeric_last(self):
        AlphanumericIdentifier.alpha_pattern = r'^[A-Z]{3}$'
        AlphanumericIdentifier.numeric_pattern = r'^[0-9]{4}$'
        AlphanumericIdentifier.seed = ['AAA', '0000']
        alpha_id = AlphanumericIdentifier('AAA99991')
        self.assertEqual(next(alpha_id), 'AAB00021')
        self.assertEqual(next(alpha_id), 'AAB00039')
        self.assertEqual(next(alpha_id), 'AAB00047')
        self.assertEqual(next(alpha_id), 'AAB00055')

    def test_increment_for_alphanumeric(self):
        AlphanumericIdentifier.alpha_pattern = r'^[A-Z]{3}$'
        AlphanumericIdentifier.numeric_pattern = r'^[0-9]{4}$'
        AlphanumericIdentifier.seed = ['AAA', '0000']
        instance = AlphanumericIdentifier(None)
        self.assertEquals(instance.identifier, 'AAA00015')
        for n in range(10000):
            identifier = next(instance)
            if n >= 9998:
                self.assertEqual('AAB', identifier[0:3])
            else:
                self.assertEqual('AAA', identifier[0:3],
                                 'Expected AAA for {}nth iteration. Got {}'.format(n, identifier))

    def test_alphanumeric_with_prefix(self):
        AlphanumericIdentifier.alpha_pattern = r'^[A-Z]{3}$'
        AlphanumericIdentifier.numeric_pattern = r'^[0-9]{4}$'
        AlphanumericIdentifier.seed = ['AAA', '0000']
        instance = AlphanumericIdentifier(prefix='ERIK')
        self.assertTrue(instance.identifier.startswith('ERIK'))
