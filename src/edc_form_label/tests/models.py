from datetime import date

from django.db import models
from django.db.models.deletion import PROTECT
from edc_consent.managers import ConsentObjectsByCdefManager, CurrentSiteByCdefManager
from edc_constants.choices import YES_NO
from edc_crf.model_mixins import CrfModelMixin
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_model.models import BaseUuidModel
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_sites.model_mixins import SiteModelMixin
from edc_utils import get_utcnow
from edc_visit_schedule.model_mixins import OffScheduleModelMixin, OnScheduleModelMixin
from edc_visit_tracking.models import SubjectVisit


class SubjectConsent(
    SiteModelMixin,
    NonUniqueSubjectIdentifierFieldMixin,
    UpdatesOrCreatesRegistrationModelMixin,
    BaseUuidModel,
):
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


class MyModel(CrfModelMixin, BaseUuidModel):
    subject_visit = models.OneToOneField(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    circumcised = models.CharField(
        verbose_name="Are you circumcised?", max_length=10, choices=YES_NO
    )


class OnSchedule(SiteModelMixin, OnScheduleModelMixin, BaseUuidModel):
    class Meta(OnScheduleModelMixin.Meta):
        pass


class OffSchedule(SiteModelMixin, OffScheduleModelMixin, BaseUuidModel):
    class Meta(OffScheduleModelMixin.Meta):
        pass
