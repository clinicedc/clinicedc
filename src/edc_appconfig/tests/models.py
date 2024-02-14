from django.db import models
from django.db.models import PROTECT
from edc_constants.choices import YES_NO
from edc_crf.model_mixins import CrfModelMixin
from edc_lab.model_mixins import PanelModelMixin
from edc_metadata.model_mixins.updates import UpdatesRequisitionMetadataModelMixin
from edc_model.models import BaseUuidModel
from edc_visit_tracking.models import SubjectVisit


class SubjectRequisition(
    CrfModelMixin,
    PanelModelMixin,
    UpdatesRequisitionMetadataModelMixin,
    BaseUuidModel,
):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    requisition_datetime = models.DateTimeField(null=True)

    is_drawn = models.CharField(max_length=25, choices=YES_NO, null=True)

    reason_not_drawn = models.CharField(max_length=25, null=True)
