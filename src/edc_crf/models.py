from django.db import models
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_model import models as edc_models
from edc_visit_schedule.model_mixins import (
    VisitScheduleFieldsModelMixin,
    VisitCodeFieldsModelMixin,
)


class CrfStatus(
    NonUniqueSubjectIdentifierFieldMixin,
    VisitScheduleFieldsModelMixin,
    VisitCodeFieldsModelMixin,
    edc_models.BaseUuidModel,
):
    label_lower = models.CharField(max_length=150, null=True)

    class Meta(edc_models.BaseUuidModel.Meta):
        verbose_name = "CRF Status"
        verbose_name_plural = "CRF Status"
