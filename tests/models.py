from typing import Any

from django.db import models
from django.db.models import Manager
from django.db.models.deletion import CASCADE, PROTECT
from edc_visit_schedule_app.models import (
    OffScheduleFive,
    OffScheduleFour,
    OffScheduleSeven,
    OnScheduleFive,
    OnScheduleFour,
    OnScheduleSeven,
)

from edc_action_item.models import ActionModelMixin
from edc_adherence.model_mixins import MedicationAdherenceModelMixin
from edc_adverse_event.model_mixins import (
    AeFollowupModelMixin,
    AeInitialModelMixin,
    AesiModelMixin,
    AeSusarModelMixin,
    AeTmgModelMixin,
    DeathReportModelMixin,
    DeathReportTmgModelMixin,
    DeathReportTmgSecondModelMixin,
    HospitalizationModelMixin,
)
from edc_appointment.model_mixins import NextAppointmentCrfModelMixin
from edc_consent.field_mixins import (
    CitizenFieldsMixin,
    IdentityFieldsMixin,
    PersonalFieldsMixin,
    ReviewFieldsMixin,
    VulnerabilityFieldsMixin,
)
from edc_consent.managers import ConsentObjectsByCdefManager, CurrentSiteByCdefManager
from edc_consent.model_mixins import (
    ConsentExtensionModelMixin,
    ConsentModelMixin,
    RequiresConsentFieldsModelMixin,
)
from edc_constants.choices import YES_NO
from edc_constants.constants import YES
from edc_crf.model_mixins import (
    CrfModelMixin,
    CrfStatusModelMixin,
    CrfWithActionModelMixin,
)
from edc_identifier.model_mixins import (
    NonUniqueSubjectIdentifierFieldMixin,
    NonUniqueSubjectIdentifierModelMixin,
)
from edc_lab.model_mixins import PanelModelMixin
from edc_metadata.model_mixins.updates import UpdatesRequisitionMetadataModelMixin
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_randomization.model_mixins import RandomizationListModelMixin
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_screening.model_mixins import EligibilityModelMixin, ScreeningModelMixin
from edc_sites.managers import CurrentSiteManager
from edc_sites.model_mixins import SiteModelMixin
from edc_utils import get_utcnow
from edc_visit_schedule.constants import OFFSCHEDULE_ACTION
from edc_visit_schedule.model_mixins import (
    OffScheduleModelMixin,
    OnScheduleModelMixin,
    VisitScheduleModelMixin,
)
from edc_visit_schedule.models import VisitSchedule
from edc_visit_tracking.models import SubjectVisit
from tests.eligibility import MyScreeningEligibility

__all__ = [
    "SubjectScreening",
    "SubjectScreeningWithoutEligibility",
    "SubjectScreeningSimple",
    "SubjectConsent",
    "SubjectConsentV1",
    "SubjectConsentV1Ext",
    "SubjectConsentUgV1",
    "SubjectConsentV2",
    "SubjectConsentV3",
    "SubjectConsentV4",
    "SubjectConsentUpdateToV3",
    "SubjectReconsent",
    "SubjectConsent2",
    "SubjectRequisition",
    "CrfOne",
    "CrfTwo",
    "CrfThree",
    "CrfFour",
    "CrfFive",
    "CrfSix",
    "CrfSeven",
    "SubjectIdentifierModel",
    "OnScheduleOne",
    "OnScheduleTwo",
    "OnScheduleThree",
    "OnScheduleFour",
    "OnScheduleFive",
    "OnScheduleSix",
    "OnScheduleSeven",
    "OffScheduleOne",
    "OffScheduleTwo",
    "OffScheduleThree",
    "OffScheduleFour",
    "OffScheduleFive",
    "OffScheduleSix",
    "OffScheduleSeven",
    "TestModelWithoutMixin",
    "TestModelWithActionDoesNotCreateAction",
    "TestModelWithAction",
    "Aesi",
    "AeTmg",
    "DeathReport",
    "DeathReportTmg",
    "AeFollowup",
    "AeInitial",
    "AeSusar",
    "FormZero",
    "FormOne",
    "FormTwo",
    "FormThree",
    "FormFour",
    "Initial",
    "Followup",
    "MyAction",
    "NextAppointmentCrf",
    "CrfLongitudinalOne",
    "CrfLongitudinalTwo",
    "MedicationAdherence",
    "Hospitalization",
]


class SubjectScreening(ScreeningModelMixin, EligibilityModelMixin, BaseUuidModel):
    thing = models.CharField(max_length=10, null=True)

    eligibility_cls = MyScreeningEligibility

    alive = models.CharField(max_length=10, default=YES)

    def get_consent_definition(self):
        pass


class SubjectScreeningSimple(ScreeningModelMixin, EligibilityModelMixin, BaseUuidModel):
    def get_consent_definition(self):
        pass


class SubjectScreeningWithoutEligibility(
    ScreeningModelMixin, EligibilityModelMixin, BaseUuidModel
):

    def get_consent_definition(self):
        pass


class SubjectConsent(
    ConsentModelMixin,
    SiteModelMixin,
    NonUniqueSubjectIdentifierModelMixin,
    UpdatesOrCreatesRegistrationModelMixin,
    IdentityFieldsMixin,
    ReviewFieldsMixin,
    PersonalFieldsMixin,
    CitizenFieldsMixin,
    VulnerabilityFieldsMixin,
    BaseUuidModel,
):
    screening_identifier = models.CharField(
        verbose_name="Screening identifier", max_length=50, unique=True
    )
    history = HistoricalRecords()

    class Meta(ConsentModelMixin.Meta):
        pass


class SubjectConsentV1(SubjectConsent):
    on_site = CurrentSiteByCdefManager()
    objects = ConsentObjectsByCdefManager()

    class Meta:
        proxy = True


class SubjectConsentV1Ext(ConsentExtensionModelMixin, SiteModelMixin, BaseUuidModel):

    subject_consent = models.ForeignKey(SubjectConsentV1, on_delete=models.PROTECT)

    on_site = CurrentSiteManager()
    history = HistoricalRecords()
    objects = Manager()

    class Meta(ConsentExtensionModelMixin.Meta, BaseUuidModel.Meta):
        verbose_name = "Subject Consent Extension V1.1"
        verbose_name_plural = "Subject Consent Extension V1.1"


class SubjectConsentUgV1(SubjectConsent):
    on_site = CurrentSiteByCdefManager()
    objects = ConsentObjectsByCdefManager()

    class Meta:
        proxy = True


class SubjectConsentV2(SubjectConsent):
    on_site = CurrentSiteByCdefManager()
    objects = ConsentObjectsByCdefManager()

    class Meta:
        proxy = True


class SubjectConsentV3(SubjectConsent):
    on_site = CurrentSiteByCdefManager()
    objects = ConsentObjectsByCdefManager()

    class Meta:
        proxy = True


class SubjectConsentV4(SubjectConsent):
    on_site = CurrentSiteByCdefManager()
    objects = ConsentObjectsByCdefManager()

    class Meta:
        proxy = True


class SubjectConsentUpdateToV3(SubjectConsent):
    class Meta:
        proxy = True


class SubjectReconsent(
    ConsentModelMixin,
    SiteModelMixin,
    NonUniqueSubjectIdentifierModelMixin,
    UpdatesOrCreatesRegistrationModelMixin,
    IdentityFieldsMixin,
    ReviewFieldsMixin,
    PersonalFieldsMixin,
    CitizenFieldsMixin,
    VulnerabilityFieldsMixin,
    BaseUuidModel,
):
    screening_identifier = models.CharField(
        verbose_name="Screening identifier", max_length=50, unique=True
    )
    history = HistoricalRecords()

    class Meta(ConsentModelMixin.Meta):
        pass


class SubjectConsent2(
    ConsentModelMixin,
    SiteModelMixin,
    NonUniqueSubjectIdentifierModelMixin,
    UpdatesOrCreatesRegistrationModelMixin,
    IdentityFieldsMixin,
    ReviewFieldsMixin,
    PersonalFieldsMixin,
    CitizenFieldsMixin,
    VulnerabilityFieldsMixin,
    BaseUuidModel,
):
    screening_identifier = models.CharField(
        verbose_name="Screening identifier", max_length=50, unique=True
    )

    history = HistoricalRecords()

    class Meta(ConsentModelMixin.Meta):
        pass


class SubjectVisitWithoutAppointment(
    SiteModelMixin,
    RequiresConsentFieldsModelMixin,
    VisitScheduleModelMixin,
    BaseUuidModel,
):
    subject_identifier = models.CharField(max_length=25)
    report_datetime = models.DateTimeField(default=get_utcnow)

    class Meta(BaseUuidModel.Meta):
        pass


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


class SubjectIdentifierModelManager(models.Manager):
    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)


class SubjectIdentifierModel(NonUniqueSubjectIdentifierFieldMixin, BaseUuidModel):
    objects = SubjectIdentifierModelManager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.subject_identifier,)  # noqa

    class Meta(BaseUuidModel.Meta, NonUniqueSubjectIdentifierFieldMixin.Meta):
        pass


class OnScheduleOne(SiteModelMixin, OnScheduleModelMixin, BaseUuidModel):
    pass


class OffScheduleOne(SiteModelMixin, OffScheduleModelMixin, BaseUuidModel):
    class Meta(OffScheduleModelMixin.Meta):
        pass


class OnScheduleTwo(SiteModelMixin, OnScheduleModelMixin, BaseUuidModel):
    pass


class OffScheduleTwo(SiteModelMixin, OffScheduleModelMixin, BaseUuidModel):
    pass


class OnScheduleThree(SiteModelMixin, OnScheduleModelMixin, BaseUuidModel):
    pass


class OffScheduleThree(SiteModelMixin, OffScheduleModelMixin, BaseUuidModel):
    pass


class OnScheduleSix(SiteModelMixin, OnScheduleModelMixin, BaseUuidModel):
    pass


class OffScheduleSix(SiteModelMixin, OffScheduleModelMixin, BaseUuidModel):
    pass


class OffSchedule(
    SiteModelMixin, ActionModelMixin, OffScheduleModelMixin, BaseUuidModel
):
    action_name = OFFSCHEDULE_ACTION
    offschedule_compare_dates_as_datetimes = False

    class Meta(OffScheduleModelMixin.Meta, BaseUuidModel.Meta):
        verbose_name = "Off-schedule"
        verbose_name_plural = "Off-schedule"


class TestModelWithoutMixin(BaseUuidModel):
    subject_identifier = models.CharField(max_length=25)
    history = HistoricalRecords()


class TestModelWithActionDoesNotCreateAction(
    NonUniqueSubjectIdentifierFieldMixin,
    ActionModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):
    action_name = "test-nothing-prn-action"


class TestModelWithAction(
    NonUniqueSubjectIdentifierFieldMixin,
    ActionModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):
    action_name = "submit-form-zero"


# edc-action-item
class FormZero(
    NonUniqueSubjectIdentifierFieldMixin,
    ActionModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):
    action_name = "submit-form-zero"

    f1 = models.CharField(max_length=100, null=True)


class FormOne(
    NonUniqueSubjectIdentifierFieldMixin,
    ActionModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):
    action_name = "submit-form-one"

    f1 = models.CharField(max_length=100, null=True)


class FormTwo(
    NonUniqueSubjectIdentifierFieldMixin,
    ActionModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):
    form_one = models.ForeignKey(FormOne, on_delete=PROTECT)

    action_name = "submit-form-two"


class FormThree(
    NonUniqueSubjectIdentifierFieldMixin,
    ActionModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):
    action_name = "submit-form-three"


class FormFour(
    NonUniqueSubjectIdentifierFieldMixin,
    ActionModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):
    action_name = "submit-form-four"

    happy = models.CharField(max_length=10, choices=YES_NO, default=YES)


class Initial(
    NonUniqueSubjectIdentifierFieldMixin,
    ActionModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):
    action_name = "submit-initial"


class Followup(
    NonUniqueSubjectIdentifierFieldMixin,
    ActionModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):
    initial = models.ForeignKey(Initial, on_delete=CASCADE)

    action_name = "submit-followup"


class MyAction(
    NonUniqueSubjectIdentifierFieldMixin,
    ActionModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):
    action_name = "my-action"


class CrfOne(ActionModelMixin, CrfStatusModelMixin, SiteModelMixin, BaseUuidModel):
    subject_visit = models.OneToOneField(
        "edc_visit_tracking.subjectvisit",  # noqa
        on_delete=CASCADE,
        related_name="edc_action_item_test_visit_one",
    )

    report_datetime = models.DateTimeField(default=get_utcnow)

    action_name = "submit-crf-one"

    @property
    def subject_identifier(self: Any) -> str:
        return self.subject_visit.subject_identifier

    @property
    def related_visit(self):
        return getattr(self, self.related_visit_model_attr())

    @classmethod
    def related_visit_model_attr(cls):
        return "subject_visit"


class CrfTwo(ActionModelMixin, CrfStatusModelMixin, SiteModelMixin, BaseUuidModel):
    subject_visit = models.OneToOneField(
        "edc_visit_tracking.subjectvisit",  # noqa
        on_delete=CASCADE,
        related_name="edc_action_item_test_visit_two",
    )

    action_name = "submit-crf-two"

    @property
    def subject_identifier(self: Any) -> str:
        return self.subject_visit.subject_identifier

    @property
    def related_visit(self):
        return getattr(self, self.related_visit_model_attr())

    @classmethod
    def related_visit_model_attr(cls):
        return "subject_visit"


class CrfThree(CrfModelMixin, CrfStatusModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    f1 = models.CharField(max_length=50, null=True, blank=True)

    f2 = models.CharField(max_length=50, null=True, blank=True)

    f3 = models.CharField(max_length=50, null=True, blank=True)

    allow_create_interim = models.BooleanField(default=False)

    appt_date = models.DateField(null=True, blank=True)


class CrfFour(CrfModelMixin, CrfStatusModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    f1 = models.CharField(max_length=50, null=True, blank=True)

    f2 = models.CharField(max_length=50, null=True, blank=True)

    f3 = models.CharField(max_length=50, null=True, blank=True)


class CrfFive(CrfModelMixin, CrfStatusModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    f1 = models.CharField(max_length=50, null=True, blank=True)

    f2 = models.CharField(max_length=50, null=True, blank=True)

    f3 = models.CharField(max_length=50, null=True, blank=True)


class CrfSix(CrfModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    f1 = models.CharField(max_length=50, null=True, blank=True)

    f2 = models.CharField(max_length=50, null=True, blank=True)

    f3 = models.CharField(max_length=50, null=True, blank=True)

    next_appt_date = models.DateField(null=True, blank=True)

    next_visit_code = models.CharField(max_length=50, null=True, blank=True)


class CrfSeven(CrfModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    f1 = models.CharField(max_length=50, null=True, blank=True)

    f2 = models.CharField(max_length=50, null=True, blank=True)

    f3 = models.CharField(max_length=50, null=True, blank=True)

    visitschedule = models.ForeignKey(
        VisitSchedule, on_delete=PROTECT, max_length=15, null=True, blank=False
    )


class CrfEight(CrfModelMixin, CrfStatusModelMixin, BaseUuidModel):
    """Crf use SubjectVisit without appointment"""

    subject_visit = models.ForeignKey(SubjectVisitWithoutAppointment, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    f1 = models.CharField(max_length=50, null=True, blank=True)

    f2 = models.CharField(max_length=50, null=True, blank=True)

    f3 = models.CharField(max_length=50, null=True, blank=True)

    @property
    def related_visit(self):
        return self.subject_visit


class NextAppointmentCrf(NextAppointmentCrfModelMixin, CrfModelMixin, BaseUuidModel):
    pass


class CrfLongitudinalOne(
    CrfWithActionModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):
    action_name = "submit-crf-longitudinal-one"

    f1 = models.CharField(max_length=50, null=True)

    f2 = models.CharField(max_length=50, null=True)

    f3 = models.CharField(max_length=50, null=True)


class CrfLongitudinalTwo(
    CrfWithActionModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):
    action_name = "submit-crf-longitudinal-two"

    f1 = models.CharField(max_length=50, null=True)

    f2 = models.CharField(max_length=50, null=True)

    f3 = models.CharField(max_length=50, null=True)


# edc-adherence
class MedicationAdherence(MedicationAdherenceModelMixin, CrfModelMixin, BaseUuidModel):

    missed_pill_reason = models.ManyToManyField(
        "edc_adherence.NonAdherenceReasons",
        verbose_name="Reasons for missing study pills",
        blank=True,
    )

    class Meta(CrfModelMixin.Meta, BaseUuidModel.Meta):
        verbose_name = "Medication Adherence"
        verbose_name_plural = "Medication Adherence"


class AeInitial(AeInitialModelMixin, BaseUuidModel):
    class Meta(AeInitialModelMixin.Meta):
        pass


class AeFollowup(AeFollowupModelMixin, BaseUuidModel):
    ae_initial = models.ForeignKey(AeInitial, on_delete=PROTECT)

    class Meta(AeFollowupModelMixin.Meta):
        pass


class Aesi(AesiModelMixin, BaseUuidModel):
    ae_initial = models.ForeignKey(AeInitial, on_delete=PROTECT)

    class Meta(AesiModelMixin.Meta):
        pass


class AeSusar(AeSusarModelMixin, BaseUuidModel):
    ae_initial = models.ForeignKey(AeInitial, on_delete=PROTECT)

    class Meta(AeSusarModelMixin.Meta):
        pass


class AeTmg(AeTmgModelMixin, BaseUuidModel):
    ae_initial = models.ForeignKey(AeInitial, on_delete=PROTECT)

    class Meta(AeTmgModelMixin.Meta):
        pass


class DeathReport(DeathReportModelMixin, BaseUuidModel):
    # pdf_report_cls = DeathPdfReport

    class Meta(DeathReportModelMixin.Meta, BaseUuidModel.Meta):
        indexes = DeathReportModelMixin.Meta.indexes + BaseUuidModel.Meta.indexes


class DeathReportTmg(DeathReportTmgModelMixin, BaseUuidModel):
    class Meta(DeathReportTmgModelMixin.Meta):
        pass


class DeathReportTmgSecond(DeathReportTmgSecondModelMixin, DeathReportTmg):
    class Meta(DeathReportTmgSecondModelMixin.Meta):
        proxy = True


class Hospitalization(
    HospitalizationModelMixin, ActionModelMixin, SiteModelMixin, BaseUuidModel
):
    class Meta(HospitalizationModelMixin.Meta):
        pass


# edc-auth


class PiiModel(models.Model):
    name = models.CharField(max_length=50, null=True)

    class Meta:
        permissions = (("be_happy", "Can be happy"),)


class AuditorModel(models.Model):
    name = models.CharField(max_length=50, null=True)

    class Meta:
        permissions = (("be_sad", "Can be sad"),)


class AuditUuidModelMixin:
    pass


class TestModel(AuditUuidModelMixin, BaseUuidModel):
    name = models.CharField(max_length=50, null=True)
    report_datetime = models.DateTimeField(default=get_utcnow)


class TestModel2(AuditUuidModelMixin, BaseUuidModel):
    name = models.CharField(max_length=50, null=True)
    report_datetime = models.DateTimeField(default=get_utcnow)


class TestModelPermissions(AuditUuidModelMixin, BaseUuidModel):
    name = models.CharField(max_length=50, null=True)
    report_datetime = models.DateTimeField(default=get_utcnow)


class CustomRandomizationList(RandomizationListModelMixin, BaseUuidModel):
    pass
