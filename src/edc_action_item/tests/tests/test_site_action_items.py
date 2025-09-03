from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, tag

from edc_action_item.get_action_type import get_action_type
from edc_action_item.models import ActionType
from edc_action_item.site_action_items import (
    AlreadyRegistered,
    SiteActionError,
    site_action_items,
)
from tests.action_items import FormZeroAction

from ..test_case_mixin import TestCaseMixin

utc_tz = ZoneInfo("UTC")


@tag("action_item")
@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=utc_tz))
class TestSiteActionItems(TestCaseMixin, TestCase):
    def setUp(self):
        self.subject_identifier = self.fake_enroll()
        site_action_items.registry = {}
        get_action_type(FormZeroAction)
        self.action_type = ActionType.objects.get(name=FormZeroAction.name)

    def test_action_raises_if_not_registered(self):
        self.assertRaises(
            SiteActionError, FormZeroAction, subject_identifier=self.subject_identifier
        )

    def test_action_raises_if_already_registered(self):
        site_action_items.register(FormZeroAction)
        self.assertRaises(AlreadyRegistered, site_action_items.register, FormZeroAction)

    def test_action_instance_creates_action_type(self):
        ActionType.objects.all().delete()
        self.assertRaises(
            ObjectDoesNotExist, ActionType.objects.get, name=FormZeroAction.name
        )
        site_action_items.register(FormZeroAction)
        FormZeroAction(subject_identifier=self.subject_identifier)
        try:
            ActionType.objects.get(name=FormZeroAction.name)
        except ObjectDoesNotExist:
            self.fail("Object unexpectedly does not exist.")
