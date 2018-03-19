from django.db.models.deletion import CASCADE
from django.db import models
from edc_base.model_mixins import BaseUuidModel

from ..model_mixins import ActionModelMixin
from .action_items import TestPrnAction, TestDoNothingPrnAction, FormZeroAction
from .action_items import FormTwoAction, InitialAction, FollowupAction
from .action_items import FormThreeAction, FormOneAction


class SubjectIdentifierModel(BaseUuidModel):

    subject_identifier = models.CharField(
        max_length=25)


class TestModel(ActionModelMixin, BaseUuidModel):

    action_cls = None

    subject_identifier = models.CharField(
        max_length=25)

    tracking_identifier = models.CharField(
        max_length=25)


class TestModelWithTrackingIdentifierButNoActionClass(ActionModelMixin,
                                                      BaseUuidModel):

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


class TestModelWithActionWithoutTrackingIdentifier(ActionModelMixin,
                                                   BaseUuidModel):

    subject_identifier = models.CharField(
        max_length=25)

    action_cls = TestPrnAction


class TestModelWithActionDoesNotCreateAction(ActionModelMixin,
                                             BaseUuidModel):

    tracking_identifier_prefix = 'AA'

    subject_identifier = models.CharField(
        max_length=25)

    action_cls = TestDoNothingPrnAction


class TestModelWithAction(ActionModelMixin, BaseUuidModel):

    tracking_identifier_prefix = 'AA'

    subject_identifier = models.CharField(
        max_length=25)

    action_cls = FormZeroAction


class FormZero(ActionModelMixin, BaseUuidModel):

    tracking_identifier_prefix = 'AA'

    subject_identifier = models.CharField(
        max_length=25)

    action_cls = FormZeroAction


class FormOne(ActionModelMixin, BaseUuidModel):

    tracking_identifier_prefix = 'AA'

    action_cls = FormOneAction


class FormTwo(ActionModelMixin, BaseUuidModel):

    tracking_identifier_prefix = 'BB'

    subject_identifier = models.CharField(
        max_length=25)

    form_one = models.ForeignKey(FormOne, on_delete=CASCADE)

    action_cls = FormTwoAction


class FormThree(ActionModelMixin, BaseUuidModel):

    tracking_identifier_prefix = 'CC'

    subject_identifier = models.CharField(
        max_length=25)

    action_cls = FormThreeAction


class Initial(ActionModelMixin, BaseUuidModel):

    tracking_identifier_prefix = 'II'

    subject_identifier = models.CharField(
        max_length=25)

    action_cls = InitialAction


class Followup(ActionModelMixin, BaseUuidModel):

    tracking_identifier_prefix = 'FF'

    subject_identifier = models.CharField(
        max_length=25)

    initial = models.ForeignKey(Initial, on_delete=CASCADE)

    action_cls = FollowupAction
