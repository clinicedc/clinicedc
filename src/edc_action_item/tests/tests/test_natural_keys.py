from django.test import TestCase
from edc_test_utils.natural_key_test_helper import NaturalKeyTestHelper

from edc_action_item.site_action_items import site_action_items

from ..test_case_mixin import TestCaseMixin


class TestNaturalKey(TestCaseMixin, TestCase):
    natural_key_helper = NaturalKeyTestHelper()

    def setUp(self):
        self.subject_identifier = self.fake_enroll()
        site_action_items.registry = {}

    def test_natural_key_attrs(self):
        self.natural_key_helper.nk_test_natural_key_attr(
            "edc_action_item", exclude_models=["edc_action_item.subjectidentifiermodel"]
        )

    def test_get_by_natural_key_attr(self):
        self.natural_key_helper.nk_test_get_by_natural_key_attr(
            "edc_action_item", exclude_models=["edc_action_item.subjectidentifiermodel"]
        )

    # def test_deserialize_action_item(self):
    #     site_action_items.register(FormOneAction)
    #     get_action_type(FormOneAction)
    #     action = FormOneAction(subject_identifier=self.subject_identifier)
    #     action_item = ActionItem.objects.get(action_identifier=action.action_identifier)
    #     for outgoing_transaction in OutgoingTransaction.objects.filter(
    #         tx_name=action_item._meta.label_lower
    #     ):
    #         self.offline_test_helper.offline_test_deserialize(
    #             action_item, outgoing_transaction
    #         )
