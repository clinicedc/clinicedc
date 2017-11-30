from django.test import TestCase, tag

from ..exceptions import CheckDigitError
from ..identifier_with_checkdigit import IdentifierWithCheckdigit


class TestIdentifierWithCheckdigit(TestCase):

    def test_identifier_with_checkdigit(self):
        for identifier in ['18', '26', '34']:
            last_identifier = None
            with self.subTest(identifier=identifier):
                instance = IdentifierWithCheckdigit(
                    last_identifier=last_identifier)
                self.assertEqual(identifier, instance.identifier)
                last_identifier = instance.identifier

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

    @tag('3')
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
        """Asserts raises an exception if cannot split based
        on the pattern and identifier.

        Note, checkdigit_pattern does not match.
        """
        class DummyIdentifierWithCheckDigit(IdentifierWithCheckdigit):

            checkdigit_pattern = r'^[0-9]{2}$'

            def calculate_checkdigit(self, identifier):
                return '54'

        instance = DummyIdentifierWithCheckDigit()
        identifier_with_checkdigit = '98765-4'
        self.assertRaises(
            CheckDigitError, instance.remove_checkdigit, identifier_with_checkdigit)
