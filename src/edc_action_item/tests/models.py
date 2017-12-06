from django.db import models
from edc_base.model_mixins import BaseUuidModel

from ..model_mixins import ActionItemModelMixin
from ..action import Action
from edc_identifier.model_mixins import TrackingIdentifierModelMixin
from edc_action_item.action_items import ReminderAction, FormTwoAction,\
    FormThreeAction, FormOneAction
from django.db.models.deletion import CASCADE


class TestDoNothingPrnAction(Action):

    name = 'test-prn-action'
    display_name = 'Test Prn Action'


class TestPrnAction(Action):

    name = 'test-prn-action'
    display_name = 'Test Prn Action'

    def creates_action_items(self):
        return [ReminderAction]


class SubjectIdentifierModel(BaseUuidModel):

    subject_identifier = models.CharField(
        max_length=25)


class TestModel(BaseUuidModel):

    subject_identifier = models.CharField(
        max_length=25)


class TestModelWithTrackingIdentifierButNoActionClass(ActionItemModelMixin, BaseUuidModel):

    action_cls = None

    subject_identifier = models.CharField(
        max_length=25)

    tracking_identifier = models.CharField(
        max_length=25)


class TestModelWithoutMixin(BaseUuidModel):

    subject_identifier = models.CharField(
        max_length=25)

    tracking_identifier = models.CharField(
        max_length=25)


class TestModelWithActionWithoutTrackingIdentifier(ActionItemModelMixin,
                                                   BaseUuidModel):

    subject_identifier = models.CharField(
        max_length=25)

    action_cls = TestPrnAction


class TestModelWithActionDoesNotCreateAction(ActionItemModelMixin,
                                             TrackingIdentifierModelMixin,
                                             BaseUuidModel):

    tracking_identifier_prefix = 'AA'

    subject_identifier = models.CharField(
        max_length=25)

    action_cls = TestDoNothingPrnAction


class TestModelWithAction(ActionItemModelMixin,
                          TrackingIdentifierModelMixin,
                          BaseUuidModel):

    tracking_identifier_prefix = 'AA'

    subject_identifier = models.CharField(
        max_length=25)

    action_cls = ReminderAction


class FormOne(ActionItemModelMixin,
              TrackingIdentifierModelMixin,
              BaseUuidModel):

    tracking_identifier_prefix = 'AA'

    subject_identifier = models.CharField(
        max_length=25)

    action_cls = FormOneAction


class FormTwo(ActionItemModelMixin,
              TrackingIdentifierModelMixin,
              BaseUuidModel):

    tracking_identifier_prefix = 'BB'

    subject_identifier = models.CharField(
        max_length=25)

    form_one = models.ForeignKey(FormOne, on_delete=CASCADE)

    action_cls = FormTwoAction


class FormThree(ActionItemModelMixin,
                TrackingIdentifierModelMixin,
                BaseUuidModel):

    tracking_identifier_prefix = 'CC'

    subject_identifier = models.CharField(
        max_length=25)

    action_cls = FormThreeAction
