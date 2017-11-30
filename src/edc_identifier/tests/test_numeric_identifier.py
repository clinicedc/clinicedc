from django.test import TestCase, tag

from ..exceptions import IdentifierError
from ..numeric_identifier import NumericIdentifier, NumericIdentifierWithModulus


class TestNumericIdentifier(TestCase):

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
        NumericIdentifierWithModulus.checkdigit_pattern = r'^\-[0-9]{1,2}$'
        NumericIdentifierWithModulus.seed = '1000000010'
        numeric_identifier = NumericIdentifierWithModulus(None)
        self.assertEqual(numeric_identifier.identifier, '1000000011-6')
        self.assertEqual(next(numeric_identifier), '1000000012-4')

    def test_numeric_modulus_with_separator(self):
        NumericIdentifierWithModulus.separator = '-'
        NumericIdentifierWithModulus.identifier_pattern = r'^[0-9]{4}\-[0-9]{4}$'
        NumericIdentifierWithModulus.checkdigit_pattern = r'^\-[0-9]{1,2}$'
        NumericIdentifierWithModulus.seed = '1000-0000'
        numeric_identifier = NumericIdentifierWithModulus(None)
        self.assertEqual(numeric_identifier.identifier, '1000-0001-7')
        self.assertEqual(next(numeric_identifier), '1000-0002-12')
