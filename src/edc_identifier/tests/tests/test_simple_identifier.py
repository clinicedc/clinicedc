from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, override_settings, tag

from edc_identifier.models import IdentifierModel
from edc_identifier.simple_identifier import SimpleIdentifier, SimpleUniqueIdentifier

utc_tz = ZoneInfo("UTC")


@tag("identifier")
@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=utc_tz))
@override_settings(SITE_ID=30)
class TestSimpleIdentifier(TestCase):
    def test_simple(self):
        obj = SimpleIdentifier()
        self.assertIsNotNone(obj.identifier)

    def test_simple_unique(self):
        obj = SimpleUniqueIdentifier()
        self.assertIsNotNone(obj.identifier)
        try:
            IdentifierModel.objects.get(identifier=obj.identifier)
        except ObjectDoesNotExist:
            self.fail("Identifier not add to history")
