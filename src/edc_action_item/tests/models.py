from django.db import models
from django.db.models.deletion import CASCADE, PROTECT
from edc_base.model_mixins import BaseUuidModel

from ..models import ActionModelMixin


class SubjectIdentifierModel(BaseUuidModel):

    subject_identifier = models.CharField(
        max_length=25)


class TestModel(ActionModelMixin, BaseUuidModel):

    action_name = None

    tracking_identifier = models.CharField(
        max_length=25)


class TestModelWithTrackingIdentifierButNoActionClass(ActionModelMixin,
                                                      BaseUuidModel):

    action_name = None

    tracking_identifier = models.CharField(
        max_length=25)


class TestModelWithoutMixin(BaseUuidModel):

    subject_identifier = models.CharField(
        max_length=25)

    tracking_identifier = models.CharField(
        max_length=25)


class TestModelWithActionWithoutTrackingIdentifier(ActionModelMixin,
                                                   BaseUuidModel):

    action_name = 'test-prn-action'


class TestModelWithActionDoesNotCreateAction(ActionModelMixin,
                                             BaseUuidModel):

    tracking_identifier_prefix = 'AA'

    action_name = 'test-nothing-prn-action'


class TestModelWithAction(ActionModelMixin, BaseUuidModel):

    tracking_identifier_prefix = 'AA'

    action_name = 'submit-form-zero'


class FormZero(ActionModelMixin, BaseUuidModel):

    tracking_identifier_prefix = 'AA'

    action_name = 'submit-form-zero'


class FormOne(ActionModelMixin, BaseUuidModel):

    tracking_identifier_prefix = 'AA'

    action_name = 'submit-form-one'


class FormTwo(ActionModelMixin, BaseUuidModel):

    tracking_identifier_prefix = 'BB'

    form_one = models.ForeignKey(FormOne, on_delete=PROTECT)

    action_name = 'submit-form-two'


class FormThree(ActionModelMixin, BaseUuidModel):

    tracking_identifier_prefix = 'CC'

    action_name = 'submit-form-three'


class Initial(ActionModelMixin, BaseUuidModel):

    tracking_identifier_prefix = 'II'

    action_name = 'submit-initial'


class Followup(ActionModelMixin, BaseUuidModel):

    tracking_identifier_prefix = 'FF'

    initial = models.ForeignKey(Initial, on_delete=CASCADE)

    action_name = 'submit-followup'


class MyAction(ActionModelMixin, BaseUuidModel):

    tracking_identifier_prefix = 'MA'

    action_name = 'my-action'
