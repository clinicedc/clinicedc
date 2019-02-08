from django.db import models
from django.db.models.deletion import PROTECT
from edc_base.model_mixins import BaseUuidModel
from edc_base import get_utcnow
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_visit_tracking.model_mixins import CrfModelMixin
from edc_appointment.tests.models import SubjectVisit

from ..model_mixins import (
    OffstudyModelMixin,
    OffstudyCrfModelMixin,
    OffstudyNonCrfModelMixin,
)


class CrfOne(OffstudyCrfModelMixin, CrfModelMixin, BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    f1 = models.CharField(max_length=50, null=True, blank=True)

    f2 = models.CharField(max_length=50, null=True, blank=True)

    f3 = models.CharField(max_length=50, null=True, blank=True)


class NonCrfOne(
    NonUniqueSubjectIdentifierFieldMixin, OffstudyNonCrfModelMixin, BaseUuidModel
):

    offstudy_model = "edc_offstudy.subjectoffstudy"
    report_datetime = models.DateTimeField(default=get_utcnow)


class BadNonCrfOne(
    NonUniqueSubjectIdentifierFieldMixin, OffstudyNonCrfModelMixin, BaseUuidModel
):

    offstudy_model = None
    report_datetime = models.DateTimeField(default=get_utcnow)


class SubjectOffstudy2(OffstudyModelMixin, BaseUuidModel):

    pass
