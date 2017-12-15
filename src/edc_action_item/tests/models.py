from django.db.models.deletion import CASCADE
from django.db import models
from edc_base.model_mixins import BaseUuidModel
from edc_identifier.model_mixins import TrackingIdentifierModelMixin

from ..model_mixins import ActionItemModelMixin
from .action_items import TestPrnAction, TestDoNothingPrnAction, FormZeroAction
from .action_items import ReminderAction, FormTwoAction, FormThreeAction, FormOneAction


class SubjectIdentifierModel(BaseUuidModel):

    subject_identifier = models.CharField(
        max_length=25)


class TestModel(ActionItemModelMixin, BaseUuidModel):

    action_cls = None

    subject_identifier = models.CharField(
        max_length=25)

    tracking_identifier = models.CharField(
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


class FormZero(ActionItemModelMixin,
               TrackingIdentifierModelMixin,
               BaseUuidModel):

    tracking_identifier_prefix = 'AA'

    subject_identifier = models.CharField(
        max_length=25)

    action_cls = FormZeroAction


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
