from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from faker import Faker

from edc_identifier.models import IdentifierModel
from edc_identifier.short_identifier import (
    DuplicateIdentifierError,
    ShortIdentifier,
    ShortIdentifierPrefixError,
    ShortIdentifierPrefixPatternError,
)

fake = Faker()


class TestShortIdentifier(TestCase):
    def setUp(self):
        edc_device_app_config = django_apps.get_app_config("edc_device")
        self.device_id = edc_device_app_config.device_id

    def test_short_identifier(self):
        short_identifier = ShortIdentifier(prefix_pattern="^[0-9]{2}$", prefix=22)
        self.assertIsNotNone(short_identifier.identifier)

    def test_short_identifier_str(self):
        short_identifier = ShortIdentifier(prefix_pattern="^[0-9]{2}$", prefix=22)
        self.assertEqual(str(short_identifier), short_identifier.identifier)

    def test_short_identifier_invalid_prefix_pattern(self):
        self.assertRaises(
            ShortIdentifierPrefixPatternError,
            ShortIdentifier,
            prefix_pattern="[0-9]{2}",
            prefix=22,
        )

    def test_short_identifier_invalid_prefix(self):
        self.assertRaises(
            ShortIdentifierPrefixError,
            ShortIdentifier,
            prefix_pattern="^[0-9]{2}$",
            prefix="AA",
        )

    def test_short_identifier_needs_prefix_if_pattern(self):
        self.assertRaises(
            ShortIdentifierPrefixError,
            ShortIdentifier,
            prefix_pattern="^[0-9]{2}$",
            prefix=None,
        )

    def test_short_identifier_needs_prefix_pattern_if_prefix(self):
        class NewCls(ShortIdentifier):
            prefix_pattern = None

        self.assertRaises(ShortIdentifierPrefixError, NewCls, prefix_pattern=None, prefix=22)

    def test_short_identifier_prefix_pattern_must_match_prefix(self):
        self.assertRaises(
            ShortIdentifierPrefixError,
            ShortIdentifier,
            prefix_pattern="^[0-9]{2}$",
            prefix="AA",
        )

    def test_short_identifier_identifier_model(self):
        short_identifier = ShortIdentifier(prefix_pattern="^[0-9]{2}$", prefix=22)
        self.assertEqual(str(short_identifier), short_identifier.identifier)

    def test_short_identifier_longer_than_default(self):
        prefix = "222"
        random_string_length = 7
        prefix_pattern = "^[0-9]{3}$"
        short_identifier = ShortIdentifier(
            prefix_pattern=prefix_pattern,
            prefix=prefix,
            random_string_length=random_string_length,
        )
        self.assertEqual(len(short_identifier.identifier), 10)

    def test_short_identifier_history(self):
        short_identifier = ShortIdentifier(prefix_pattern="^[0-9]{2}$", prefix=22)
        try:
            IdentifierModel.objects.get(identifier=short_identifier.identifier),
        except ObjectDoesNotExist:
            self.fail("ObjectDoesNotExist unexpectedly raised")

    def test_short_identifier_with_last1(self):
        prefix = "22"
        IdentifierModel.objects.create(
            identifier="22KVTB4",
            identifier_type=ShortIdentifier.name,
            identifier_prefix=prefix,
            device_id=self.device_id,
        )

        short_identifier = ShortIdentifier(prefix_pattern="^[0-9]{2}$", prefix=prefix)
        self.assertNotEqual(short_identifier.identifier, "22KVTB4")

    def test_short_identifier_with_last2(self):
        prefix = "22"
        random_string_length = 5
        prefix_pattern = "^[0-9]{2}$"

        IdentifierModel.objects.create(
            identifier="22KVTB4",
            identifier_type=ShortIdentifier.name,
            identifier_prefix=prefix,
            device_id=self.device_id,
        )

        short_identifier = ShortIdentifier(
            prefix_pattern=prefix_pattern,
            prefix=prefix,
            random_string_length=random_string_length,
        )

        self.assertEqual(len(short_identifier.identifier), 7)

    def test_short_identifier_catches_duplicate_limit1(self):
        """Asserts raises if a duplicate identifier is generated."""
        options = dict(random_string_pattern=r"[AB]+", random_string_length=3)
        n = 1
        tries = 100
        while n < tries:
            n += 1
            try:
                ShortIdentifier(prefix="22", **options)
            except DuplicateIdentifierError:
                break
        self.assertGreater(n, 7)
        self.assertLess(n, 11)

    def test_short_identifier_catches_duplicate_limit2(self):
        """Asserts raises if a duplicate identifier is generated."""
        options = dict(random_string_pattern=r"[AB]+", random_string_length=5)
        n = 1
        tries = 100
        while n < tries:
            n += 1
            try:
                ShortIdentifier(prefix="22", **options)
            except DuplicateIdentifierError:
                break
        self.assertGreater(n, 32)
        self.assertLess(n, 35)
