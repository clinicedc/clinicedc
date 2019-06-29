from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, tag
from edc_action_item.action import ActionError
from edc_action_item.get_action_type import get_action_type
from edc_action_item.models import ActionType, ActionItem
from edc_action_item.site_action_items import (
    site_action_items,
    SiteActionError,
    AlreadyRegistered,
)
from uuid import uuid4

from ..action_items import FormZeroAction
from ..models import SubjectIdentifierModel


class TestSiteActionItems(TestCase):
    def setUp(self):
        self.subject_identifier_model = ActionItem.subject_identifier_model
        ActionItem.subject_identifier_model = "edc_action_item.subjectidentifiermodel"
        self.subject_identifier = "12345"
        SubjectIdentifierModel.objects.create(
            subject_identifier=self.subject_identifier
        )
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

    #     def test_action_raises_if_name_changed(self):
    #         class FormZeroAction1(FormZeroAction):
    #             name = str(uuid4())
    #
    #         class FormZeroAction2(FormZeroAction):
    #             name = str(uuid4())
    #
    #         site_action_items.register(FormZeroAction1)
    #         site_action_items.register(FormZeroAction2)
    #         FormZeroAction1.name = FormZeroAction2.name
    #         self.assertRaises(ActionError, FormZeroAction1)

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


#     def test_getting_action_from_registry_creates_action_type(self):
#
#         ActionType.objects.all().delete()
#         self.assertRaises(
#             ObjectDoesNotExist, ActionType.objects.get, name=FormZeroAction.name
#         )
#         site_action_items.register(FormZeroAction)
#         site_action_items.get(FormZeroAction.name)
#         try:
#             ActionType.objects.get(name=FormZeroAction.name)
#         except ObjectDoesNotExist:
#             self.fail("Object unexpectedly does not exist.")
