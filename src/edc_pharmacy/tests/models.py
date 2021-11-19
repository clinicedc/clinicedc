from django.db import models
from edc_crf.crf_model_mixin import CrfModelMixin
from edc_model import models as edc_models
from edc_pharmacy.models import StudyMedicationCrfModelMixin
from edc_sites.models import SiteModelMixin
from edc_visit_schedule.model_mixins import OffScheduleModelMixin, OnScheduleModelMixin
from edc_visit_tracking.model_mixins import VisitModelMixin


class SubjectVisit(VisitModelMixin, edc_models.BaseUuidModel):
    class Meta(VisitModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        app_label = "edc_pharmacy"


class StudyMedication(
    StudyMedicationCrfModelMixin, SiteModelMixin, edc_models.BaseUuidModel
):

    subject_visit = models.OneToOneField(SubjectVisit, on_delete=models.PROTECT)

    class Meta(CrfModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        app_label = "edc_pharmacy"


class OnSchedule(OnScheduleModelMixin, edc_models.BaseUuidModel):

    pass


class OffSchedule(OffScheduleModelMixin, edc_models.BaseUuidModel):

    pass
