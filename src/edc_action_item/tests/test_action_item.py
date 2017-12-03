from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, tag
from edc_constants.constants import NEW, OPEN
from edc_list_data import site_list_data


from ..forms import ActionItemForm
from ..models import ActionItem, ActionItemUpdate, SubjectDoesNotExist, ActionType
from .models import SubjectIdentifierModel


class TestActionItem(TestCase):

    @classmethod
    def setUpClass(cls):
        site_list_data.autodiscover()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        self.subject_identifier_model = ActionItem.subject_identifier_model
        ActionItem.subject_identifier_model = 'edc_action_item.subjectidentifiermodel'
        self.subject_identifier = '12345'
        SubjectIdentifierModel.objects.create(
            subject_identifier=self.subject_identifier)
        self.action_type = ActionType.objects.all().first()

    def tearDown(self):
        ActionItem.subject_identifier_model = self.subject_identifier_model

    def test_create(self):
        self.assertRaises(
            SubjectDoesNotExist,
            ActionItem.objects.create)
        obj = ActionItem.objects.create(
            subject_identifier=self.subject_identifier,
            action_type=self.action_type,
            reference_model='edc_action_item.testmodel')
        self.assertTrue(obj.action_identifier.startswith('AC'))
        self.assertEqual(obj.status, NEW)
        self.assertIsNotNone(obj.report_datetime)

    def test_identifier_not_changed(self):
        obj = ActionItem.objects.create(
            subject_identifier=self.subject_identifier,
            action_type=self.action_type)
        action_identifier = obj.action_identifier
        obj.save()
        try:
            obj = ActionItem.objects.get(action_identifier=action_identifier)
        except ObjectDoesNotExist:
            self.fail('ActionItem unexpectedly does not exist')

    def test_form(self):
        obj = ActionItem.objects.create(
            subject_identifier=self.subject_identifier,
            action_type=self.action_type,
            name='a new action item')
        data = obj.__dict__
        data.update(action_type=obj.action_type.id)
        form = ActionItemForm(data=obj.__dict__, instance=obj)
        self.assertEqual(form.errors, {})

    def test_changes_status_from_new_to_open_on_edit(self):
        obj = ActionItem.objects.create(
            subject_identifier=self.subject_identifier,
            action_type=self.action_type,
            name='a new action item')
        ActionItemUpdate.objects.create(action_item=obj)
        ActionItemUpdate.objects.create(action_item=obj)
        ActionItemUpdate.objects.create(action_item=obj)
        data = obj.__dict__
        data.update(action_type=obj.action_type.id)
        data['status'] = NEW
        form = ActionItemForm(data=obj.__dict__, instance=obj)
        self.assertTrue(form.is_valid())
        self.assertNotIn('status', form.errors)
        self.assertEqual(form.cleaned_data.get('status'), OPEN)
