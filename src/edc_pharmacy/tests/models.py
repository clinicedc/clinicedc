from datetime import date

from django.db import models
from edc_consent.managers import ConsentObjectsByCdefManager, CurrentSiteByCdefManager
from edc_crf.model_mixins import CrfModelMixin
from edc_identifier.managers import SubjectIdentifierManager
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_model.models import BaseUuidModel
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_screening.model_mixins import ScreeningModelMixin
from edc_sites.model_mixins import SiteModelMixin
from edc_utils import get_utcnow
from edc_visit_schedule.model_mixins import OffScheduleModelMixin, OnScheduleModelMixin
from edc_visit_tracking.model_mixins import VisitModelMixin

from edc_pharmacy.model_mixins import StudyMedicationCrfModelMixin

from .consents import consent_v1


class SubjectConsent(
    SiteModelMixin,
    NonUniqueSubjectIdentifierFieldMixin,
    UpdatesOrCreatesRegistrationModelMixin,
    BaseUuidModel,
):
    report_datetime = models.DateTimeField(default=get_utcnow)

    consent_datetime = models.DateTimeField(default=get_utcnow)

    version = models.CharField(max_length=25, default="1")

    identity = models.CharField(max_length=25)

    confirm_identity = models.CharField(max_length=25)

    dob = models.DateField(default=date(1995, 1, 1))


class SubjectConsentV1(SubjectConsent):
    objects = ConsentObjectsByCdefManager()
    on_site = CurrentSiteByCdefManager()

    class Meta:
        proxy = True


class SubjectScreening(ScreeningModelMixin, BaseUuidModel):
    consent_definition = consent_v1
    objects = SubjectIdentifierManager()


class SubjectVisit(SiteModelMixin, VisitModelMixin, BaseUuidModel):
    def run_metadata_rules(self, **kwargs):
        pass

    def metadata_create(self):
        pass

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
