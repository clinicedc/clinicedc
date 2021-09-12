from django.db import models
from edc_dx_review.model_mixins import (
    ClinicalReviewBaselineDmModelMixin,
    ClinicalReviewBaselineModelMixin,
    ClinicalReviewDmModelMixin,
    ClinicalReviewModelMixin,
    InitialReviewModelMixin,
)
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_list_data.model_mixins import ListModelMixin
from edc_model.models import BaseUuidModel
from edc_utils import get_utcnow
from edc_visit_schedule.model_mixins import VisitCodeFieldsModelMixin


class Appointment(
    NonUniqueSubjectIdentifierFieldMixin, VisitCodeFieldsModelMixin, BaseUuidModel
):
    class Meta(BaseUuidModel.Meta):
        pass


class SubjectVisit(
    NonUniqueSubjectIdentifierFieldMixin, VisitCodeFieldsModelMixin, BaseUuidModel
):

    appointment = models.ForeignKey(Appointment, on_delete=models.PROTECT, related_name="+")

    class Meta(BaseUuidModel.Meta):
        pass


class ClinicalReview(
    ClinicalReviewDmModelMixin,
    ClinicalReviewModelMixin,
    BaseUuidModel,
):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=models.PROTECT, related_name="+")

    report_datetime = models.DateTimeField(default=get_utcnow)

    class Meta(BaseUuidModel.Meta):
        pass


class ClinicalReviewBaseline(
    ClinicalReviewBaselineDmModelMixin,
    ClinicalReviewBaselineModelMixin,
    BaseUuidModel,
):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=models.PROTECT, related_name="+")

    report_datetime = models.DateTimeField(default=get_utcnow)

    class Meta(BaseUuidModel.Meta):
        pass


class DmInitialReview(
    InitialReviewModelMixin,
    BaseUuidModel,
):

    report_datetime = models.DateTimeField(default=get_utcnow)

    class Meta(BaseUuidModel.Meta):
        pass


class ReasonsForTesting(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Reasons for Testing"
        verbose_name_plural = "Reasons for Testing"
