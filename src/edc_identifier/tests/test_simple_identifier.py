from django.test import TestCase, tag

from ..simple_identifier import SimpleIdentifier
from edc_identifier.simple_identifier import SimpleUniqueIdentifier
from edc_identifier.models import IdentifierModel
from django.core.exceptions import ObjectDoesNotExist


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
