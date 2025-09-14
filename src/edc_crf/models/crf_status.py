from django.db import models
from django.db.models import Index

from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_model.models import BaseUuidModel
from edc_visit_schedule.model_mixins import (
    VisitCodeFieldsModelMixin,
    VisitScheduleFieldsModelMixin,
)


class CrfStatus(
    NonUniqueSubjectIdentifierFieldMixin,
    VisitScheduleFieldsModelMixin,
    VisitCodeFieldsModelMixin,
    BaseUuidModel,
):
    label_lower = models.CharField(max_length=150, null=True)

    class Meta(BaseUuidModel.Meta, NonUniqueSubjectIdentifierFieldMixin.Meta):
        verbose_name = "CRF Status"
        verbose_name_plural = "CRF Status"
        indexes = (
            *BaseUuidModel.Meta.indexes,
            *NonUniqueSubjectIdentifierFieldMixin.Meta.indexes,
            Index(
                fields=[
                    "schedule_name",
                    "visit_schedule_name",
                    "visit_code",
                    "visit_code_sequence",
                ]
            ),
        )
