import uuid

from django.db import models
from django.db.models.deletion import CASCADE, PROTECT
from edc_base import get_utcnow
from edc_base.model_managers.historical_records import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel
from edc_base.sites.site_model_mixin import SiteModelMixin
from edc_constants.choices import YES_NO
from edc_constants.constants import YES

from ..models import ActionModelMixin


class SubjectIdentifierModel(BaseUuidModel):

    subject_identifier = models.CharField(
        max_length=25)

    history = HistoricalRecords()


class TestModelWithoutMixin(BaseUuidModel):

    subject_identifier = models.CharField(
        max_length=25)
    history = HistoricalRecords()


class TestModelWithActionDoesNotCreateAction(ActionModelMixin,
                                             BaseUuidModel):

    action_name = 'test-nothing-prn-action'
    history = HistoricalRecords()


class TestModelWithAction(ActionModelMixin, BaseUuidModel):

    action_name = 'submit-form-zero'
    history = HistoricalRecords()


class Appointment(BaseUuidModel):

    appt_datetime = models.DateTimeField(default=get_utcnow)
    history = HistoricalRecords()


class SubjectVisit(SiteModelMixin, BaseUuidModel):

    subject_identifier = models.CharField(
        max_length=25)

    appointment = models.OneToOneField(Appointment, on_delete=CASCADE)
    history = HistoricalRecords()


class FormZero(ActionModelMixin, SiteModelMixin, BaseUuidModel):

    action_name = 'submit-form-zero'

    f1 = models.CharField(max_length=100, null=True)

    history = HistoricalRecords(
        history_id_field=models.UUIDField(default=uuid.uuid4))


class FormOne(ActionModelMixin, SiteModelMixin, BaseUuidModel):

    action_name = 'submit-form-one'

    f1 = models.CharField(max_length=100, null=True)

    history = HistoricalRecords()


class FormTwo(ActionModelMixin, SiteModelMixin, BaseUuidModel):

    form_one = models.ForeignKey(FormOne, on_delete=PROTECT)

    action_name = 'submit-form-two'

    history = HistoricalRecords()


class FormThree(ActionModelMixin, SiteModelMixin, BaseUuidModel):

    action_name = 'submit-form-three'

    history = HistoricalRecords()


class FormFour(ActionModelMixin, SiteModelMixin, BaseUuidModel):

    action_name = 'submit-form-four'

    happy = models.CharField(
        max_length=10,
        choices=YES_NO,
        default=YES)

    history = HistoricalRecords()


class Initial(ActionModelMixin, SiteModelMixin, BaseUuidModel):

    action_name = 'submit-initial'

    history = HistoricalRecords()


class Followup(ActionModelMixin, SiteModelMixin, BaseUuidModel):

    initial = models.ForeignKey(Initial, on_delete=CASCADE)

    action_name = 'submit-followup'

    history = HistoricalRecords()


class MyAction(ActionModelMixin, SiteModelMixin, BaseUuidModel):

    action_name = 'my-action'

    history = HistoricalRecords()


class CrfOne(ActionModelMixin, SiteModelMixin, BaseUuidModel):

    subject_visit = models.OneToOneField(SubjectVisit, on_delete=CASCADE)

    action_name = 'submit-crf-one'

    history = HistoricalRecords()

    @property
    def visit(self):
        return self.subject_visit

    @classmethod
    def visit_model_attr(self):
        return 'subject_visit'


class CrfTwo(ActionModelMixin, SiteModelMixin, BaseUuidModel):

    subject_visit = models.OneToOneField(SubjectVisit, on_delete=CASCADE)

    action_name = 'submit-crf-two'

    history = HistoricalRecords()

    @property
    def visit(self):
        return self.subject_visit

    @classmethod
    def visit_model_attr(self):
        return 'subject_visit'
