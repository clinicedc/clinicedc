from django.db import models
from django.db.models.deletion import CASCADE, PROTECT
from edc_base import get_utcnow
from edc_base.model_mixins import BaseUuidModel

from ..models import ActionModelMixin


class SubjectIdentifierModel(BaseUuidModel):

    subject_identifier = models.CharField(
        max_length=25)


class TestModelWithoutMixin(BaseUuidModel):

    subject_identifier = models.CharField(
        max_length=25)


class TestModelWithActionDoesNotCreateAction(ActionModelMixin,
                                             BaseUuidModel):

    action_name = 'test-nothing-prn-action'


class TestModelWithAction(ActionModelMixin, BaseUuidModel):

    action_name = 'submit-form-zero'


class Appointment(BaseUuidModel):

    appt_datetime = models.DateTimeField(default=get_utcnow())


class SubjectVisit(BaseUuidModel):

    subject_identifier = models.CharField(
        max_length=25)

    appointment = models.OneToOneField(Appointment, on_delete=CASCADE)


class FormZero(ActionModelMixin, BaseUuidModel):

    action_name = 'submit-form-zero'


class FormOne(ActionModelMixin, BaseUuidModel):

    action_name = 'submit-form-one'


class FormTwo(ActionModelMixin, BaseUuidModel):

    form_one = models.ForeignKey(FormOne, on_delete=PROTECT)

    action_name = 'submit-form-two'


class FormThree(ActionModelMixin, BaseUuidModel):

    action_name = 'submit-form-three'


class Initial(ActionModelMixin, BaseUuidModel):

    action_name = 'submit-initial'


class Followup(ActionModelMixin, BaseUuidModel):

    initial = models.ForeignKey(Initial, on_delete=CASCADE)

    action_name = 'submit-followup'


class MyAction(ActionModelMixin, BaseUuidModel):

    action_name = 'my-action'


class CrfOne(ActionModelMixin, BaseUuidModel):

    subject_visit = models.OneToOneField(SubjectVisit, on_delete=CASCADE)

    action_name = 'submit-crf-one'

    @property
    def visit(self):
        return self.subject_visit

    @classmethod
    def visit_model_attr(self):
        return 'subject_visit'


class CrfTwo(ActionModelMixin, BaseUuidModel):

    subject_visit = models.OneToOneField(SubjectVisit, on_delete=CASCADE)

    action_name = 'submit-crf-two'

    @property
    def visit(self):
        return self.subject_visit

    @classmethod
    def visit_model_attr(self):
        return 'subject_visit'
