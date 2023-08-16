from django.db import models
from edc_constants.choices import YES_NO, YES_NO_UNKNOWN
from edc_constants.constants import NOT_APPLICABLE
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_model import models as edc_models
from edc_model.validators import date_not_future, datetime_not_future
from edc_protocol.validators import (
    date_not_before_study_start,
    datetime_not_before_study_start,
)
from edc_utils import get_utcnow


class HospitalizationModelMixin(NonUniqueSubjectIdentifierFieldMixin, models.Model):
    report_datetime = models.DateTimeField(
        verbose_name="Report Date",
        validators=[datetime_not_before_study_start, datetime_not_future],
        default=get_utcnow,
    )

    have_details = models.CharField(
        verbose_name="Do you have details of the hospitalization?",
        max_length=15,
        choices=YES_NO,
    )

    admitted_date = models.DateField(
        verbose_name="When was the patient admitted?",
        validators=[date_not_future, date_not_before_study_start],
    )

    admitted_date_estimated = edc_models.IsDateEstimatedField(
        verbose_name="Is this date estimated?",
    )

    discharged = models.CharField(
        verbose_name="Has the patient been discharged?",
        max_length=15,
        choices=YES_NO_UNKNOWN,
    )

    discharged_date = models.DateField(
        verbose_name="If YES, give date discharged",
        validators=[date_not_future, date_not_before_study_start],
        null=True,
        blank=True,
    )

    discharged_date_estimated = edc_models.IsDateEstimatedFieldNa(
        verbose_name="If YES, is this date estimated?",
        default=NOT_APPLICABLE,
    )

    narrative = models.TextField(
        verbose_name="Narrative",
        max_length=500,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
        verbose_name = "Hospitalization"
        verbose_name_plural = "Hospitalization"
