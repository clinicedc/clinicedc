from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from edc_identifier.models import IdentifierModel
from edc_identifier.simple_identifier import SimpleIdentifier, SimpleUniqueIdentifier


class TestSimpleIdentifier(TestCase):
    def test_simple(self):
        obj = SimpleIdentifier()
        obj.identifier

    def test_simple_unique(self):
        obj = SimpleUniqueIdentifier()
        self.assertIsNotNone(obj.identifier)
        try:
            IdentifierModel.objects.get(identifier=obj.identifier)
        except ObjectDoesNotExist:
            self.fail("Identifier not add to history")
