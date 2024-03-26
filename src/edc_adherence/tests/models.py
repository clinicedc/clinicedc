from django.db import models
from django.db.models import PROTECT
from edc_appointment.models import Appointment
from edc_consent.managers import ConsentObjectsByCdefManager, CurrentSiteByCdefManager
from edc_consent.model_mixins.consent_version_model_mixin import (
    ConsentVersionModelMixin,
)
from edc_crf.model_mixins import CrfModelMixin, CrfWithActionModelMixin
from edc_identifier.managers import SubjectIdentifierManager
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierModelMixin
from edc_list_data.model_mixins import ListModelMixin
from edc_metadata.model_mixins.creates import CreatesMetadataModelMixin
from edc_model.models import BaseUuidModel
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_screening.model_mixins import ScreeningModelMixin
from edc_sites.model_mixins import SiteModelMixin
from edc_utils import get_utcnow
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.model_mixins import (
    SubjectVisitMissedModelMixin,
    VisitModelMixin,
)

from edc_adherence.model_mixins import MedicationAdherenceModelMixin
from edc_adherence.tests.consents import consent_v1


class DeathReport(BaseUuidModel):
    subject_identifier = models.CharField(max_length=50)


class OffStudy(BaseUuidModel):
    subject_identifier = models.CharField(max_length=50)

    offstudy_datetime = models.DateTimeField(default=get_utcnow)


class SubjectScreening(ScreeningModelMixin, BaseUuidModel):
    consent_definition = consent_v1
    objects = SubjectIdentifierManager()


class SubjectConsent(
    SiteModelMixin,
    ConsentVersionModelMixin,
    NonUniqueSubjectIdentifierModelMixin,
    UpdatesOrCreatesRegistrationModelMixin,
    BaseUuidModel,
):
    subject_identifier = models.CharField(max_length=50)

    consent_datetime = models.DateTimeField()

    dob = models.DateTimeField(null=True)

    version = models.CharField(max_length=10)


class SubjectConsentV1(SubjectConsent):
    on_site = CurrentSiteByCdefManager()
    objects = ConsentObjectsByCdefManager()

    class Meta:
        proxy = True


class OnSchedule(SiteModelMixin, BaseUuidModel):
    subject_identifier = models.CharField(max_length=50)

    onschedule_datetime = models.DateTimeField(default=get_utcnow)


class OffSchedule(SiteModelMixin, BaseUuidModel):
    subject_identifier = models.CharField(max_length=50)

    offschedule_datetime = models.DateTimeField(default=get_utcnow)


class SubjectVisit(
    VisitModelMixin,
    CreatesMetadataModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):
    appointment = models.OneToOneField(
        Appointment, on_delete=PROTECT, related_name="edc_adherence_appointment"
    )

    subject_identifier = models.CharField(max_length=50)

    reason = models.CharField(max_length=25, default=SCHEDULED)


class SubjectVisitMissedReasons(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Subject Missed Visit Reasons"
        verbose_name_plural = "Subject Missed Visit Reasons"


class SubjectVisitMissed(
    SubjectVisitMissedModelMixin,
    CrfWithActionModelMixin,
    BaseUuidModel,
):
    missed_reasons = models.ManyToManyField(
        SubjectVisitMissedReasons, blank=True, related_name="+"
    )

    class Meta(
        SubjectVisitMissedModelMixin.Meta,
        BaseUuidModel.Meta,
    ):
        verbose_name = "Missed Visit Report"
        verbose_name_plural = "Missed Visit Report"


class MedicationAdherence(MedicationAdherenceModelMixin, CrfModelMixin, BaseUuidModel):
    class Meta(CrfModelMixin.Meta, BaseUuidModel.Meta):
        verbose_name = "Medication Adherence"
        verbose_name_plural = "Medication Adherence"
