from django.test import TestCase, tag
from django_collect_offline.models import OutgoingTransaction
from django_collect_offline.tests import OfflineTestHelper
from edc_action_item.get_action_type import get_action_type
from edc_action_item.models import ActionItem
from edc_action_item.site_action_items import site_action_items

from ..action_items import FormOneAction
from ..models import SubjectIdentifierModel


class TestNaturalKey(TestCase):

    offline_test_helper = OfflineTestHelper()

    def setUp(self):
        self.subject_identifier = "12345"
        ActionItem.subject_identifier_model = "edc_action_item.subjectidentifiermodel"
        self.subject_identifier_model = ActionItem.subject_identifier_model
        SubjectIdentifierModel.objects.create(
            subject_identifier=self.subject_identifier
        )
        site_action_items.registry = {}

    def test_natural_key_attrs(self):
        self.offline_test_helper.offline_test_natural_key_attr(
            "edc_action_item", exclude_models=["edc_action_item.subjectidentifiermodel"]
        )

    def test_get_by_natural_key_attr(self):
        self.offline_test_helper.offline_test_get_by_natural_key_attr(
            "edc_action_item", exclude_models=["edc_action_item.subjectidentifiermodel"]
        )

    def test_deserialize_action_item(self):
        site_action_items.register(FormOneAction)
        get_action_type(FormOneAction)
        action = FormOneAction(subject_identifier=self.subject_identifier)
        action_item = ActionItem.objects.get(action_identifier=action.action_identifier)
        for outgoing_transaction in OutgoingTransaction.objects.filter(
            tx_name=action_item._meta.label_lower
        ):
            self.offline_test_helper.offline_test_deserialize(
                action_item, outgoing_transaction
            )
