from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, tag
from edc_constants.constants import NEW, OPEN, CLOSED

from ..constants import RESOLVED, REJECTED, FEEDBACK
from ..forms import ActionItemForm
from ..models import ActionItem, ActionItemUpdate, SubjectDoesNotExist
from .models import SubjectIdentifierModel


class TestActionItem(TestCase):

    def setUp(self):
        self.subject_identifier_model = ActionItem.subject_identifier_model
        ActionItem.subject_identifier_model = 'edc_action_item.subjectidentifiermodel'
        self.subject_identifier = '12345'
        SubjectIdentifierModel.objects.create(
            subject_identifier=self.subject_identifier)

    def tearDown(self):
        ActionItem.subject_identifier_model = self.subject_identifier_model

    def test_create(self):
        self.assertRaises(
            SubjectDoesNotExist,
            ActionItem.objects.create)
        obj = ActionItem.objects.create(
            subject_identifier=self.subject_identifier)
        self.assertTrue(obj.action_identifier.startswith('AC'))
        self.assertEqual(obj.status, NEW)
        self.assertIsNotNone(obj.report_datetime)

    def test_identifier_not_changed(self):
        obj = ActionItem.objects.create(
            subject_identifier=self.subject_identifier)
        action_identifier = obj.action_identifier
        obj.save()
        try:
            obj = ActionItem.objects.get(action_identifier=action_identifier)
        except ObjectDoesNotExist:
            self.fail('ActionItem unexpectedly does not exist')

    def test_form(self):
        obj = ActionItem.objects.create(
            subject_identifier=self.subject_identifier,
            title='a new action item')
        form = ActionItemForm(data=obj.__dict__, instance=obj)
        self.assertEqual(form.errors, {})

    def test_changes_status_from_new_to_open_on_edit(self):
        obj = ActionItem.objects.create(
            subject_identifier=self.subject_identifier,
            title='a new action item')
        ActionItemUpdate.objects.create(action_item=obj)
        ActionItemUpdate.objects.create(action_item=obj)
        ActionItemUpdate.objects.create(action_item=obj)
        data = obj.__dict__
        data['status'] = NEW
        form = ActionItemForm(data=obj.__dict__, instance=obj)
        self.assertTrue(form.is_valid())
        self.assertNotIn('status', form.errors)
        self.assertEqual(form.cleaned_data.get('status'), OPEN)

    def test_cannot_set_to_resolved_if_open_updates(self):
        obj = ActionItem.objects.create(
            subject_identifier=self.subject_identifier,
            title='a new action item')
        ActionItemUpdate.objects.create(action_item=obj)
        ActionItemUpdate.objects.create(action_item=obj)
        ActionItemUpdate.objects.create(action_item=obj)
        data = obj.__dict__

        data['status'] = RESOLVED
        form = ActionItemForm(data=obj.__dict__, instance=obj)
        self.assertFalse(form.is_valid())
        self.assertIn('status', form.errors)

        data['status'] = CLOSED
        form = ActionItemForm(data=obj.__dict__, instance=obj)
        self.assertFalse(form.is_valid())
        self.assertIn('status', form.errors)

        data['status'] = REJECTED
        form = ActionItemForm(data=obj.__dict__, instance=obj)
        self.assertFalse(form.is_valid())
        self.assertIn('status', form.errors)

        data['status'] = FEEDBACK
        form = ActionItemForm(data=obj.__dict__, instance=obj)
        self.assertTrue(form.is_valid())
        self.assertNotIn('status', form.errors)
        self.assertEqual(form.cleaned_data.get('status'), FEEDBACK)

        data['status'] = OPEN
        form = ActionItemForm(data=obj.__dict__, instance=obj)
        self.assertTrue(form.is_valid())
        self.assertNotIn('status', form.errors)
        self.assertEqual(form.cleaned_data.get('status'), OPEN)

    def test_can_set_to_resolved_if_no_open_updates(self):
        obj = ActionItem.objects.create(
            subject_identifier=self.subject_identifier,
            title='a new action item')
        ActionItemUpdate.objects.create(action_item=obj, closed=True)
        ActionItemUpdate.objects.create(action_item=obj, closed=True)
        ActionItemUpdate.objects.create(action_item=obj, closed=True)
        data = obj.__dict__

        data['status'] = RESOLVED
        form = ActionItemForm(data=obj.__dict__, instance=obj)
        self.assertTrue(form.is_valid())
        self.assertNotIn('status', form.errors)
        self.assertEqual(form.cleaned_data.get('status'), RESOLVED)

        data['status'] = CLOSED
        form = ActionItemForm(data=obj.__dict__, instance=obj)
        self.assertTrue(form.is_valid())
        self.assertNotIn('status', form.errors)
        self.assertEqual(form.cleaned_data.get('status'), CLOSED)
