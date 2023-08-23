from django.db import models
from edc_crf.model_mixins import CrfModelMixin
from edc_identifier.managers import SubjectIdentifierManager
from edc_model.models import BaseUuidModel
from edc_screening.model_mixins import ScreeningModelMixin
from edc_sites.models import SiteModelMixin
from edc_utils import get_utcnow
from edc_visit_schedule.model_mixins import OffScheduleModelMixin, OnScheduleModelMixin
from edc_visit_tracking.model_mixins import VisitModelMixin

from edc_pharmacy.model_mixins import StudyMedicationCrfModelMixin


class SubjectScreening(ScreeningModelMixin, BaseUuidModel):
    objects = SubjectIdentifierManager()


class SubjectConsent(SiteModelMixin, BaseUuidModel):
    subject_identifier = models.CharField(max_length=25)

    consent_datetime = models.DateTimeField()

    dob = models.DateTimeField(null=True)

    class Meta:
        pass


class SubjectVisit(SiteModelMixin, VisitModelMixin, BaseUuidModel):
    class Meta(VisitModelMixin.Meta, BaseUuidModel.Meta):
        app_label = "edc_pharmacy"


class StudyMedication(
    StudyMedicationCrfModelMixin,
    CrfModelMixin,
    BaseUuidModel,
):
    subject_visit = models.OneToOneField(SubjectVisit, on_delete=models.PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    def run_metadata_rules_for_related_visit(self, **kwargs):
        pass

    def metadata_update(self, **kwargs):
        pass

    def update_reference_on_save(self):
        return None

    class Meta(CrfModelMixin.Meta, BaseUuidModel.Meta):
        app_label = "edc_pharmacy"


class OnSchedule(SiteModelMixin, OnScheduleModelMixin, BaseUuidModel):
    pass


class OffSchedule(SiteModelMixin, OffScheduleModelMixin, BaseUuidModel):
    pass
