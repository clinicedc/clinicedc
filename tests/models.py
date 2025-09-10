import uuid
from typing import Any
from uuid import uuid4

from django.db import models
from django.db.models import Manager
from django.db.models.deletion import CASCADE, PROTECT

from django_crypto_fields.fields import EncryptedCharField
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
from edc_constants.choices import YES_NO, YES_NO_NA
from edc_constants.constants import YES
from edc_crf.model_mixins import (
    CrfInlineModelMixin,
    CrfModelMixin,
    CrfStatusModelMixin,
    CrfWithActionModelMixin,
)
from edc_export.managers import ExportHistoryManager
from edc_export.model_mixins import ExportTrackingFieldsModelMixin
from edc_identifier.managers import SubjectIdentifierManager
from edc_identifier.model_mixins import (
    NonUniqueSubjectIdentifierFieldMixin,
    NonUniqueSubjectIdentifierModelMixin,
)
from edc_lab.model_mixins import CrfWithRequisitionModelMixin, RequisitionModelMixin
from edc_lab_panel.panels import fbc_panel
from edc_lab_results import BLOOD_RESULTS_FBC_ACTION
from edc_lab_results.model_mixins import (
    BloodResultsModelMixin,
    HaemoglobinModelMixin,
    Hba1cModelMixin,
    HctModelMixin,
    PlateletsModelMixin,
    RbcModelMixin,
    WbcModelMixin,
)
from edc_list_data.model_mixins import BaseListModelMixin, ListModelMixin
from edc_model import models as edc_models
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_model.validators import date_not_future, datetime_not_future
from edc_offstudy.model_mixins import OffstudyModelMixin
from edc_pharmacy.model_mixins import StudyMedicationCrfModelMixin
from edc_protocol.validators import (
    date_not_before_study_start,
    datetime_not_before_study_start,
)
from edc_randomization.model_mixins import RandomizationListModelMixin
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_reportable import GRAMS_PER_DECILITER
from edc_reportable.choices import REPORTABLE
from edc_screening.model_mixins import EligibilityModelMixin, ScreeningModelMixin
from edc_screening.screening_eligibility import ScreeningEligibility
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
from edc_visit_tracking.model_mixins import VisitTrackingCrfModelMixin
from edc_visit_tracking.models import SubjectVisit
from .eligibility import MyScreeningEligibility

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
    "OnScheduleEight",
    "OffScheduleOne",
    "OffScheduleTwo",
    "OffScheduleThree",
    "OffScheduleFour",
    "OffScheduleFive",
    "OffScheduleSix",
    "OffScheduleSeven",
    "OffScheduleEight",
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

    eligibility_cls = ScreeningEligibility

    thing = models.CharField(max_length=10, null=True)
    alive = models.CharField(max_length=10, default=YES)

    def get_consent_definition(self):
        pass


class MySubjectScreening(ScreeningModelMixin, EligibilityModelMixin, BaseUuidModel):
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


class SubjectConsentV5(SubjectConsent):
    on_site = CurrentSiteByCdefManager()
    objects = ConsentObjectsByCdefManager()

    class Meta:
        proxy = True


class SubjectConsentV6(SubjectConsent):
    on_site = CurrentSiteByCdefManager()
    objects = ConsentObjectsByCdefManager()

    class Meta:
        proxy = True


class SubjectConsentV7(SubjectConsent):
    on_site = CurrentSiteByCdefManager()
    objects = ConsentObjectsByCdefManager()

    class Meta:
        proxy = True


class SubjectConsentUpdateToV3(SubjectConsent):
    class Meta:
        proxy = True


class SubjectConsent2V1(SubjectConsent):
    on_site = CurrentSiteByCdefManager()
    objects = ConsentObjectsByCdefManager()

    class Meta:
        proxy = True


class SubjectConsent2V2(SubjectConsent):
    on_site = CurrentSiteByCdefManager()
    objects = ConsentObjectsByCdefManager()

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


class SubjectOffstudyFive(SiteModelMixin, OffstudyModelMixin, BaseUuidModel):
    objects = SubjectIdentifierManager()


class SubjectOffstudySix(SiteModelMixin, OffstudyModelMixin, BaseUuidModel):
    objects = SubjectIdentifierManager()


class SubjectOffstudySeven(SiteModelMixin, OffstudyModelMixin, BaseUuidModel):
    objects = SubjectIdentifierManager()


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


class SubjectRequisition(RequisitionModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    is_drawn = models.CharField(max_length=25, choices=YES_NO, null=True)

    reason_not_drawn = models.CharField(max_length=25, null=True)

    def update_reference_on_save(self):
        pass

    class Meta(RequisitionModelMixin.Meta, BaseUuidModel.Meta):
        pass


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


class OffSchedule(SiteModelMixin, OffScheduleModelMixin, ActionModelMixin, BaseUuidModel):
    action_name = OFFSCHEDULE_ACTION
    offschedule_compare_dates_as_datetimes = False

    class Meta(OffScheduleModelMixin.Meta, BaseUuidModel.Meta):
        verbose_name = "Off-schedule"
        verbose_name_plural = "Off-schedule"


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


class OnScheduleFour(SiteModelMixin, OnScheduleModelMixin, BaseUuidModel):
    pass


class OffScheduleFour(SiteModelMixin, OffScheduleModelMixin, BaseUuidModel):
    pass


class OnScheduleFive(SiteModelMixin, OnScheduleModelMixin, BaseUuidModel):
    pass


class OffScheduleFive(SiteModelMixin, OffScheduleModelMixin, BaseUuidModel):
    offschedule_datetime_field_attr: str = "my_offschedule_datetime"
    my_offschedule_datetime = models.DateTimeField(
        verbose_name="Date and time subject taken off schedule",
        validators=[datetime_not_before_study_start, datetime_not_future],
        default=get_utcnow,
    )


class OnScheduleSix(SiteModelMixin, OnScheduleModelMixin, BaseUuidModel):
    pass


class OffScheduleSix(SiteModelMixin, OffScheduleModelMixin, BaseUuidModel):
    offschedule_datetime_field_attr: str = "my_offschedule_date"

    my_offschedule_date = models.DateField(
        verbose_name="Date subject taken off schedule",
        validators=[date_not_before_study_start, date_not_future],
        default=get_utcnow,
    )


class OnScheduleSeven(SiteModelMixin, OnScheduleModelMixin, BaseUuidModel):
    pass


class OffScheduleSeven(SiteModelMixin, OffScheduleModelMixin, BaseUuidModel):
    pass


class OnScheduleEight(SiteModelMixin, OnScheduleModelMixin, BaseUuidModel):
    pass


class OffScheduleEight(SiteModelMixin, OffScheduleModelMixin, BaseUuidModel):
    pass


class BadOffSchedule1(SiteModelMixin, OffScheduleModelMixin, BaseUuidModel):
    """Meta.OffScheduleModelMixin.offschedule_datetime_field
    is None.
    """

    offschedule_datetime_field_attr = None

    my_offschedule_date = models.DateField()

    class Meta(OffScheduleModelMixin.Meta):
        pass


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


class Alphabet(models.Model):
    display_name = models.CharField(max_length=25, null=True)

    name = models.CharField(max_length=25, null=True)


class ListModel(ListModelMixin):
    pass


class ListOne(BaseListModelMixin, BaseUuidModel):
    char1 = models.CharField(max_length=25, null=True)

    dte = models.DateTimeField(default=get_utcnow)


class ListTwo(BaseListModelMixin, BaseUuidModel):
    char1 = models.CharField(max_length=25, null=True)

    dte = models.DateTimeField(default=get_utcnow)


class CrfEncrypted(CrfModelMixin, ExportTrackingFieldsModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    encrypted1 = EncryptedCharField(null=True)

    export_history = ExportHistoryManager()


class Crf(CrfModelMixin, ExportTrackingFieldsModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    char1 = models.CharField(max_length=25, null=True)

    date1 = models.DateTimeField(null=True)

    int1 = models.IntegerField(null=True)

    uuid1 = models.UUIDField(null=True)

    m2m = models.ManyToManyField(ListModel)

    export_history = ExportHistoryManager()


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

    f4 = models.IntegerField(null=True, blank=True)

    f5 = models.UUIDField(null=True, blank=True)

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

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    f1 = models.CharField(max_length=50, null=True, blank=True)

    f2 = models.CharField(max_length=50, null=True, blank=True)

    f3 = models.CharField(max_length=50, null=True, blank=True)

    @property
    def related_visit(self):
        return self.subject_visit


class CrfOneProxyOne(CrfOne):
    class Meta:
        proxy = True


class CrfOneProxyTwo(CrfOne):
    class Meta:
        proxy = True


class CrfOneProxyThree(CrfOne):
    class Meta:
        proxy = True


class CrfTwoProxyOne(CrfTwo):
    class Meta:
        proxy = True


class CrfTwoProxyTwo(CrfTwo):
    class Meta:
        proxy = True


class CrfWithInline(CrfModelMixin, BaseUuidModel):
    list_one = models.ForeignKey(ListOne, on_delete=models.PROTECT)

    list_two = models.ForeignKey(ListTwo, on_delete=models.PROTECT)

    char1 = models.CharField(max_length=25, null=True)

    dte = models.DateTimeField(default=get_utcnow)


class CrfWithInline2(BaseUuidModel):
    crf_one = models.ForeignKey(CrfOne, on_delete=models.PROTECT)

    crf_two = models.ForeignKey(CrfTwo, on_delete=models.PROTECT)

    dte = models.DateTimeField(default=get_utcnow)


class CrfOneInline(CrfInlineModelMixin, BaseUuidModel):
    crf_one = models.ForeignKey(CrfOne, on_delete=PROTECT)

    other_model = models.ForeignKey(Alphabet, on_delete=PROTECT)

    f1 = models.CharField(max_length=10, default="erik")

    def natural_key(self) -> tuple:
        return tuple()

    class Meta(CrfInlineModelMixin.Meta):
        crf_inline_parent = "crf_one"


class BadCrfOneInline(CrfInlineModelMixin, BaseUuidModel):
    """A model class missing _meta.crf_inline_parent."""

    crf_one = models.ForeignKey(CrfOne, on_delete=PROTECT)

    other_model = models.ForeignKey(Alphabet, on_delete=PROTECT)

    f1 = models.CharField(max_length=10, default="erik")

    def natural_key(self) -> tuple:
        return tuple()

    class Meta:
        pass


class BadCrfNoRelatedVisit(SiteModelMixin, VisitTrackingCrfModelMixin, BaseUuidModel):
    subject_visit = None

    f1 = models.CharField(max_length=50, null=True)

    f2 = models.CharField(max_length=50, null=True)

    f3 = models.CharField(max_length=50, null=True)

    class Meta(BaseUuidModel.Meta):
        pass


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


class TestModel(BaseUuidModel):
    name = models.CharField(verbose_name="What is your name?", max_length=50, null=True)
    report_datetime = models.DateTimeField(default=get_utcnow)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Test Model"


class TestModel2(BaseUuidModel):
    name = models.CharField(verbose_name="What is your name?", max_length=50, null=True)
    report_datetime = models.DateTimeField(default=get_utcnow)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Test Model2"


class TestModelPermissions(BaseUuidModel):
    name = models.CharField(max_length=50, null=True)
    report_datetime = models.DateTimeField(default=get_utcnow)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Test Model Permissions"


class TestModel3(CrfModelMixin, BaseUuidModel):

    report_datetime = models.DateTimeField(default=get_utcnow)

    f1 = models.CharField(verbose_name="Is it what it is?", max_length=10, choices=YES_NO)

    f2 = models.CharField(
        verbose_name="Are they serious?", max_length=10, null=True, blank=True
    )

    f3 = models.CharField(
        verbose_name="Are you worried?", max_length=10, null=True, blank=False
    )

    f4 = models.CharField(
        verbose_name="Would they dare?", max_length=10, null=True, blank=False
    )

    f5 = models.CharField(
        verbose_name="What am I going to tell them?",
        max_length=10,
        null=True,
        blank=False,
    )

    summary_one = models.CharField(
        verbose_name="summary_one", max_length=10, null=True, blank=True
    )

    summary_two = models.CharField(
        verbose_name="summary_two", max_length=10, null=True, blank=True
    )


class TestModel4(CrfModelMixin, BaseUuidModel):

    report_datetime = models.DateTimeField(default=get_utcnow)

    f1 = models.CharField(verbose_name="Is it what it is?", max_length=10, choices=YES_NO)

    f2 = models.CharField(
        verbose_name="Are they serious?", max_length=10, null=True, blank=True
    )

    f3 = models.CharField(
        verbose_name="Are you worried?", max_length=10, null=True, blank=False
    )

    f4 = models.CharField(
        verbose_name="Would they dare?", max_length=10, null=True, blank=False
    )

    f5 = models.CharField(
        verbose_name="What am I going to tell them?",
        max_length=10,
        null=True,
        blank=False,
    )

    summary_one = models.CharField(
        verbose_name="summary_one", max_length=10, null=True, blank=True
    )

    summary_two = models.CharField(
        verbose_name="summary_two", max_length=10, null=True, blank=True
    )


class TestModel5(CrfModelMixin, BaseUuidModel):
    subject_visit = models.OneToOneField(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    circumcised = models.CharField(
        verbose_name="Are you circumcised?", max_length=10, choices=YES_NO
    )


class TestModel6(TestModel3):
    class Meta:
        proxy = True


class TestModelWithFk(models.Model):
    f1 = models.CharField(max_length=10)
    f2 = models.CharField(max_length=10)
    f3 = models.CharField(max_length=10, null=True, blank=False)
    f4 = models.CharField(max_length=10, null=True, blank=False)
    f5 = models.CharField(max_length=10)
    f5_other = models.CharField(max_length=10, null=True)
    alphabet = models.ManyToManyField(Alphabet)

    class Meta:
        verbose_name = "Test model"
        verbose_name_plural = "Test models"


class CustomRandomizationList(RandomizationListModelMixin, BaseUuidModel):
    pass


class Prn(SiteModelMixin, BaseUuidModel):
    subject_identifier = models.CharField(max_length=50, null=True, blank=True)

    report_datetime = models.DateTimeField(default=get_utcnow)

    f1 = models.CharField(max_length=50, null=True, blank=True)

    f2 = models.CharField(max_length=50, null=True, blank=True)

    f3 = models.CharField(max_length=50, null=True, blank=True)

    class Meta(BaseUuidModel.Meta):
        pass


class PrnOne(CrfModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT, related_name="+")

    report_datetime = models.DateTimeField(default=get_utcnow)

    f1 = models.CharField(max_length=50, null=True, blank=True)


class PrnTwo(CrfModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT, related_name="+")

    report_datetime = models.DateTimeField(default=get_utcnow)

    f1 = models.CharField(max_length=50, null=True, blank=True)


class PrnThree(CrfModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT, related_name="+")

    report_datetime = models.DateTimeField(default=get_utcnow)

    f1 = models.CharField(max_length=50, null=True, blank=True)


class Team(CrfModelMixin, BaseUuidModel):

    name = models.CharField(max_length=36, default=uuid4)

    class Meta(CrfModelMixin.Meta, BaseUuidModel.Meta):
        verbose_name = "Team"
        verbose_name_plural = "Teams"


class Venue(CrfModelMixin, BaseUuidModel):

    name = models.CharField(max_length=36, default=uuid4)

    class Meta(CrfModelMixin.Meta, BaseUuidModel.Meta):
        verbose_name = "Venue"
        verbose_name_plural = "Venues"


class Member(SiteModelMixin, BaseUuidModel):

    team = models.ForeignKey(Team, on_delete=PROTECT)

    player_name = models.CharField(max_length=36, default=uuid4)

    skill_level = models.CharField(max_length=36, default=uuid4)

    @property
    def subject_identifier(self):
        return self.team.subject_visit.subject_identifier

    @property
    def visit_code(self):
        return self.team.subject_visit.visit_code

    @property
    def visit_code_sequence(self):
        return self.team.subject_visit.visit_code_sequence

    class Meta(SiteModelMixin.Meta, BaseUuidModel.Meta):
        verbose_name = "Member"
        verbose_name_plural = "Members"


class TeamWithDifferentFields(CrfModelMixin, BaseUuidModel):

    size = models.IntegerField()

    name = models.CharField(max_length=36, null=True, blank=False)

    color = models.CharField(max_length=36, null=True, blank=False)

    mood = models.CharField(max_length=36, default="good")

    class Meta(CrfModelMixin.Meta, BaseUuidModel.Meta):
        verbose_name = "TeamWithDifferentFields"
        verbose_name_plural = "TeamWithDifferentFields"


class SubjectModelOne(UpdatesOrCreatesRegistrationModelMixin, BaseUuidModel):
    screening_identifier = models.CharField(max_length=25, null=True)

    registration_identifier = models.UUIDField(unique=True, default=uuid.uuid4)

    dob = models.DateField(null=True)

    @property
    def registration_unique_field(self):
        return "registration_identifier"


class SubjectModelTwo(UpdatesOrCreatesRegistrationModelMixin, BaseUuidModel):
    """Note: registration_unique_field is overridden."""

    subject_identifier = models.CharField(max_length=25, null=True)

    dob = models.DateField(null=True)

    @property
    def registration_unique_field(self):
        return "subject_identifier"


class SubjectModelThree(UpdatesOrCreatesRegistrationModelMixin, BaseUuidModel):
    """Note: registration_unique_field is overridden."""

    subject_identifier = models.CharField(max_length=25, null=True)

    my_identifier = models.UUIDField(default=uuid.uuid4)

    dob = models.DateField(null=True)

    @property
    def registration_unique_field(self):
        return "my_identifier"

    @property
    def registered_model_unique_field(self):
        return "registration_identifier"


class CrfMissingManager(BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    f1 = models.CharField(max_length=50, null=True)


class SpecimenResult(CrfModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=CASCADE)

    report_datetime = models.DateTimeField(default=get_utcnow)

    haemoglobin = models.DecimalField(decimal_places=1, max_digits=6, null=True, blank=True)

    haemoglobin_units = models.CharField(
        verbose_name="units",
        max_length=10,
        choices=((GRAMS_PER_DECILITER, GRAMS_PER_DECILITER),),
        null=True,
        blank=True,
    )

    haemoglobin_abnormal = models.CharField(
        verbose_name="abnormal", choices=YES_NO, max_length=25, null=True, blank=True
    )

    haemoglobin_reportable = models.CharField(
        verbose_name="reportable",
        choices=REPORTABLE,
        max_length=25,
        null=True,
        blank=True,
    )

    results_abnormal = models.CharField(
        verbose_name="Are any of the above results abnormal?",
        choices=YES_NO,
        max_length=25,
    )

    results_reportable = models.CharField(
        verbose_name="If any results are abnormal, are results within grade III " "or above?",
        max_length=25,
        choices=YES_NO_NA,
    )

    @property
    def abnormal(self):
        return self.results_abnormal

    @property
    def reportable(self):
        return self.results_reportable


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
        pass


class RedirectNextModel(BaseUuidModel):
    subject_identifier = models.CharField(max_length=25)


class BloodResultsFbc(
    CrfWithActionModelMixin,
    CrfWithRequisitionModelMixin,
    HaemoglobinModelMixin,
    HctModelMixin,
    RbcModelMixin,
    WbcModelMixin,
    PlateletsModelMixin,
    BloodResultsModelMixin,
    edc_models.BaseUuidModel,
):
    action_name = BLOOD_RESULTS_FBC_ACTION

    tracking_identifier_prefix = "FB"

    lab_panel = fbc_panel

    class Meta(CrfWithActionModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "Blood Result: FBC"
        verbose_name_plural = "Blood Results: FBC"


# this model does not include the requisition and action item mixins
class BloodResultsHba1c(
    CrfModelMixin,
    CrfWithRequisitionModelMixin,
    Hba1cModelMixin,
    BloodResultsModelMixin,
    edc_models.BaseUuidModel,
):
    class Meta(edc_models.BaseUuidModel.Meta):
        verbose_name = "HbA1c"
        verbose_name_plural = "HbA1c"
