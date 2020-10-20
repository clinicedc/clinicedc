from django.db import models
from django.db.models.deletion import PROTECT
from edc_constants.constants import HOSPITALIZED, OTHER
from edc_crf.model_mixins import CrfModelMixin
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_list_data.model_mixins import ListModelMixin
from edc_metadata.model_mixins.creates import CreatesMetadataModelMixin
from edc_model.models import BaseUuidModel
from edc_offstudy.model_mixins import OffstudyModelMixin
from edc_reference.model_mixins import ReferenceModelMixin
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_sites.models import SiteModelMixin
from edc_utils import get_utcnow
from edc_visit_schedule.model_mixins import (
    OnScheduleModelMixin,
    OffScheduleModelMixin,
)

from ..choices import VISIT_REASON, VISIT_REASON_MISSED, VISIT_INFO_SOURCE
from ..model_mixins import (
    CrfInlineModelMixin,
    SubjectVisitMissedModelMixin,
    VisitTrackingCrfModelMixin,
    VisitModelMixin,
)
from ..models import SubjectVisitMissedReasons

list_data = {
    "edc_visit_tracking.subjectvisitmissedreasons": [
        ("forgot", "Forgot / Can’t remember being told about appointment"),
        ("family_emergency", "Family emergency (e.g. funeral) and was away"),
        ("travelling", "Away travelling/visiting"),
        ("working_schooling", "Away working/schooling"),
        ("too_sick", "Too sick or weak to come to the centre"),
        ("lack_of_transport", "Transportation difficulty"),
        (HOSPITALIZED, "Hospitalized"),
        (OTHER, "Other reason (specify below)"),
    ],
}


class SubjectConsent(
    NonUniqueSubjectIdentifierFieldMixin,
    UpdatesOrCreatesRegistrationModelMixin,
    BaseUuidModel,
):
    consent_datetime = models.DateTimeField(default=get_utcnow)

    report_datetime = models.DateTimeField(default=get_utcnow)


class OnScheduleOne(OnScheduleModelMixin, BaseUuidModel):
    pass


class OnScheduleTwo(OnScheduleModelMixin, BaseUuidModel):
    pass


class OffSchedule(OffScheduleModelMixin, BaseUuidModel):
    pass


class OffScheduleOne(OffScheduleModelMixin, BaseUuidModel):
    pass


class SubjectOffstudy(OffstudyModelMixin, BaseUuidModel):
    class Meta(OffstudyModelMixin.Meta):
        pass


class SubjectVisit(
    VisitModelMixin,
    ReferenceModelMixin,
    CreatesMetadataModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):
    reason = models.CharField(max_length=25, choices=VISIT_REASON)

    reason_missed = models.CharField(
        verbose_name="If 'missed', provide the reason for the missed visit",
        max_length=35,
        choices=VISIT_REASON_MISSED,
        blank=True,
        null=True,
    )

    info_source = models.CharField(
        verbose_name="What is the main source of this information?",
        max_length=25,
        choices=VISIT_INFO_SOURCE,
    )

    class Meta(VisitModelMixin.Meta, BaseUuidModel.Meta):
        pass


class CrfOne(VisitTrackingCrfModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    f1 = models.CharField(max_length=50, null=True)

    f2 = models.CharField(max_length=50, null=True)

    f3 = models.CharField(max_length=50, null=True)


class OtherModel(BaseUuidModel):
    f1 = models.CharField(max_length=10, default="erik")


class CrfOneInline(CrfInlineModelMixin, BaseUuidModel):
    crf_one = models.ForeignKey(CrfOne, on_delete=PROTECT)

    other_model = models.ForeignKey(OtherModel, on_delete=PROTECT)

    f1 = models.CharField(max_length=10, default="erik")

    class Meta(CrfInlineModelMixin.Meta):
        crf_inline_parent = "crf_one"


class BadCrfOneInline(CrfInlineModelMixin, BaseUuidModel):
    """A model class missing _meta.crf_inline_parent.
    """

    crf_one = models.ForeignKey(CrfOne, on_delete=PROTECT)

    other_model = models.ForeignKey(OtherModel, on_delete=PROTECT)

    f1 = models.CharField(max_length=10, default="erik")

    class Meta:
        pass


class BadCrfOneInline2(CrfInlineModelMixin, BaseUuidModel):
    crf_one = models.ForeignKey(CrfOne, on_delete=PROTECT)

    other_model = models.ForeignKey(OtherModel, on_delete=PROTECT)

    f1 = models.CharField(max_length=10, default="erik")

    class Meta(CrfInlineModelMixin.Meta):
        crf_inline_parent = None


class CustomSubjectVisitMissedReasons(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Subject Visit Missed Reason"
        verbose_name_plural = "Subject Visit Missed Reasons"


class SubjectVisitMissed(
    CrfModelMixin, SubjectVisitMissedModelMixin, BaseUuidModel,
):
    missed_reasons = models.ManyToManyField(SubjectVisitMissedReasons, blank=True)

    class Meta(VisitTrackingCrfModelMixin.Meta):
        pass
