from django.db import models
from django.db.models.deletion import PROTECT
from edc_consent.managers import ConsentObjectsByCdefManager, CurrentSiteByCdefManager
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_model.models import BaseUuidModel
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_sites.model_mixins import SiteModelMixin
from edc_utils import get_utcnow
from edc_visit_schedule.model_mixins import OffScheduleModelMixin, OnScheduleModelMixin
from edc_visit_tracking.model_mixins import VisitTrackingCrfModelMixin
from edc_visit_tracking.models import SubjectVisit

from ..model_mixins import (
    OffstudyCrfModelMixin,
    OffstudyModelMixin,
    OffstudyNonCrfModelMixin,
)


class SubjectConsent(
    SiteModelMixin,
    NonUniqueSubjectIdentifierFieldMixin,
    UpdatesOrCreatesRegistrationModelMixin,
    BaseUuidModel,
):
    consent_datetime = models.DateTimeField(default=get_utcnow)

    report_datetime = models.DateTimeField(default=get_utcnow)

    version = models.CharField(max_length=10, default="1")

    dob = models.DateField()

    class Meta(BaseUuidModel.Meta):
        pass


class SubjectConsentV1(SubjectConsent):
    objects = ConsentObjectsByCdefManager()
    on_site = CurrentSiteByCdefManager()

    class Meta:
        proxy = True


class OnScheduleOne(SiteModelMixin, OnScheduleModelMixin, BaseUuidModel):
    class Meta(BaseUuidModel.Meta):
        pass


class OffScheduleOne(SiteModelMixin, OffScheduleModelMixin, BaseUuidModel):
    class Meta(BaseUuidModel.Meta):
        pass


class CrfOne(SiteModelMixin, OffstudyCrfModelMixin, VisitTrackingCrfModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    f1 = models.CharField(max_length=50, null=True, blank=True)

    f2 = models.CharField(max_length=50, null=True, blank=True)

    f3 = models.CharField(max_length=50, null=True, blank=True)


class NonCrfOne(
    SiteModelMixin,
    NonUniqueSubjectIdentifierFieldMixin,
    OffstudyNonCrfModelMixin,
    BaseUuidModel,
):
    report_datetime = models.DateTimeField(default=get_utcnow)

    class Meta(OffstudyNonCrfModelMixin.Meta):
        pass


class SubjectOffstudy2(SiteModelMixin, OffstudyModelMixin, BaseUuidModel):
    pass
