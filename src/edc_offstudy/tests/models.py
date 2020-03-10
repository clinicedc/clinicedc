from django.db import models
from django.db.models.deletion import PROTECT
from edc_appointment.tests.models import SubjectVisit, SubjectOffstudy
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_model.models import BaseUuidModel
from edc_utils import get_utcnow
from edc_visit_tracking.model_mixins import VisitTrackingCrfModelMixin

from ..model_mixins import (
    OffstudyModelMixin,
    OffstudyCrfModelMixin,
    OffstudyNonCrfModelMixin,
)


class CrfOne(OffstudyCrfModelMixin, VisitTrackingCrfModelMixin, BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    f1 = models.CharField(max_length=50, null=True, blank=True)

    f2 = models.CharField(max_length=50, null=True, blank=True)

    f3 = models.CharField(max_length=50, null=True, blank=True)


class NonCrfOne(
    NonUniqueSubjectIdentifierFieldMixin, OffstudyNonCrfModelMixin, BaseUuidModel
):

    report_datetime = models.DateTimeField(default=get_utcnow)

    class Meta(OffstudyNonCrfModelMixin.Meta):
        offstudy_model_cls = SubjectOffstudy


class BadNonCrfOne(
    NonUniqueSubjectIdentifierFieldMixin, OffstudyNonCrfModelMixin, BaseUuidModel
):

    report_datetime = models.DateTimeField(default=get_utcnow)

    class Meta(OffstudyNonCrfModelMixin.Meta):
        pass


class SubjectOffstudy2(OffstudyModelMixin, BaseUuidModel):

    pass
