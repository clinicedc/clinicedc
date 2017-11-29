from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from edc_constants.constants import NEW

from ..models import ActionItem, ActionItemUpdate, ActionItemUpdatesRequireFollowup
from ..constants import RESOLVED


class TestActionItem(TestCase):

    def test_create(self):
        obj = ActionItem.objects.create()
        self.assertTrue(obj.action_identifier.startswith('AC'))
        self.assertEqual(obj.status, NEW)
        self.assertIsNotNone(obj.report_datetime)

    def test_identifier_not_changed(self):
        obj = ActionItem.objects.create()
        action_identifier = obj.action_identifier
        obj.save()
        try:
            obj = ActionItem.objects.get(action_identifier=action_identifier)
        except ObjectDoesNotExist:
            self.fail('ActionItem unexpectedly does not exist')

    def test_resolved(self):
        obj = ActionItem.objects.create()
        ActionItemUpdate.objects.create(action_item=obj)
        ActionItemUpdate.objects.create(action_item=obj)
        ActionItemUpdate.objects.create(action_item=obj)
        obj.status = RESOLVED
        self.assertRaises(ActionItemUpdatesRequireFollowup, obj.save)
