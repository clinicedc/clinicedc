from typing import Any

from django.db import models
from django.db.models.deletion import CASCADE, PROTECT
from edc_constants.choices import YES_NO
from edc_constants.constants import YES
from edc_crf.crf_with_action_model_mixin import CrfWithActionModelMixin
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_sites.models import SiteModelMixin

from ..models import ActionModelMixin


class SubjectIdentifierModelManager(models.Manager):
    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)


class SubjectIdentifierModel(NonUniqueSubjectIdentifierFieldMixin, BaseUuidModel):

    objects = SubjectIdentifierModelManager()

    history = HistoricalRecords()

    def natural_key(self):
        return tuple(
            self.subject_identifier,
        )


class TestModelWithoutMixin(BaseUuidModel):

    subject_identifier = models.CharField(max_length=25)
    history = HistoricalRecords()


class TestModelWithActionDoesNotCreateAction(
    NonUniqueSubjectIdentifierFieldMixin,
    ActionModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):

    action_name = "test-nothing-prn-action"


class TestModelWithAction(
    NonUniqueSubjectIdentifierFieldMixin,
    ActionModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):

    action_name = "submit-form-zero"


# class SubjectVisit(VisitModelMixin, SiteModelMixin, BaseUuidModel):
#
#     appointment = models.OneToOneField(
#         "edc_appointment.appointment", on_delete=PROTECT, related_name="D_NHJS34"
#     )
#
#     report_datetime = models.DateTimeField(default=get_utcnow)
#
#     reason = models.CharField(max_length=25, default=SCHEDULED)
#
#     history = HistoricalRecords()


class FormZero(
    NonUniqueSubjectIdentifierFieldMixin,
    ActionModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):

    action_name = "submit-form-zero"

    f1 = models.CharField(max_length=100, null=True)


class FormOne(
    NonUniqueSubjectIdentifierFieldMixin,
    ActionModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):

    action_name = "submit-form-one"

    f1 = models.CharField(max_length=100, null=True)


class FormTwo(
    NonUniqueSubjectIdentifierFieldMixin,
    ActionModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):

    form_one = models.ForeignKey(FormOne, on_delete=PROTECT)

    action_name = "submit-form-two"


class FormThree(
    NonUniqueSubjectIdentifierFieldMixin,
    ActionModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):

    action_name = "submit-form-three"


class FormFour(
    NonUniqueSubjectIdentifierFieldMixin,
    ActionModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):

    action_name = "submit-form-four"

    happy = models.CharField(max_length=10, choices=YES_NO, default=YES)


class Initial(
    NonUniqueSubjectIdentifierFieldMixin,
    ActionModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):

    action_name = "submit-initial"


class Followup(
    NonUniqueSubjectIdentifierFieldMixin,
    ActionModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):

    initial = models.ForeignKey(Initial, on_delete=CASCADE)

    action_name = "submit-followup"


class MyAction(
    NonUniqueSubjectIdentifierFieldMixin,
    ActionModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):

    action_name = "my-action"


class CrfOne(ActionModelMixin, SiteModelMixin, BaseUuidModel):

    subject_visit = models.OneToOneField(
        "edc_metadata.subjectvisit",  # noqa
        on_delete=CASCADE,
        related_name="edc_action_item_test_visit_one",
    )

    action_name = "submit-crf-one"

    @property
    def subject_identifier(self: Any) -> str:
        return self.subject_visit.subject_identifier

    @property
    def visit(self):
        return self.subject_visit

    @classmethod
    def visit_model_attr(cls):
        return "subject_visit"


class CrfTwo(ActionModelMixin, SiteModelMixin, BaseUuidModel):

    subject_visit = models.OneToOneField(
        "edc_metadata.subjectvisit",  # noqa
        on_delete=CASCADE,
        related_name="edc_action_item_test_visit_two",
    )

    action_name = "submit-crf-two"

    @property
    def subject_identifier(self: Any) -> str:
        return self.subject_visit.subject_identifier

    @property
    def visit(self):
        return self.subject_visit

    @classmethod
    def visit_model_attr(cls):
        return "subject_visit"


class CrfLongitudinalOne(
    CrfWithActionModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):
    action_name = "submit-crf-longitudinal-one"

    f1 = models.CharField(max_length=50, null=True)

    f2 = models.CharField(max_length=50, null=True)

    f3 = models.CharField(max_length=50, null=True)


class CrfLongitudinalTwo(
    CrfWithActionModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):
    action_name = "submit-crf-longitudinal-two"

    f1 = models.CharField(max_length=50, null=True)

    f2 = models.CharField(max_length=50, null=True)

    f3 = models.CharField(max_length=50, null=True)
