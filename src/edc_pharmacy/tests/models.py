from django.db import models
from edc_crf.model_mixins import CrfModelMixin
from edc_model import models as edc_models
from edc_sites.models import SiteModelMixin
from edc_utils import get_utcnow
from edc_visit_schedule.model_mixins import OffScheduleModelMixin, OnScheduleModelMixin
from edc_visit_tracking.model_mixins import VisitModelMixin

from edc_pharmacy.model_mixins import StudyMedicationCrfModelMixin


class SubjectConsent(edc_models.BaseUuidModel):
    subject_identifier = models.CharField(max_length=25)

    consent_datetime = models.DateTimeField()

    class Meta:
        pass


class SubjectVisit(VisitModelMixin, edc_models.BaseUuidModel):
    class Meta(VisitModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        app_label = "edc_pharmacy"


class StudyMedication(
    StudyMedicationCrfModelMixin,
    CrfModelMixin,
    SiteModelMixin,
    edc_models.BaseUuidModel,
):

    subject_visit = models.OneToOneField(SubjectVisit, on_delete=models.PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    def run_metadata_rules_for_crf(self):
        pass

    def metadata_update(self, **kwargs):
        pass

    def update_reference_on_save(self):
        return None

    class Meta(CrfModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        app_label = "edc_pharmacy"


class OnSchedule(OnScheduleModelMixin, edc_models.BaseUuidModel):

    pass


class OffSchedule(OffScheduleModelMixin, edc_models.BaseUuidModel):

    pass
