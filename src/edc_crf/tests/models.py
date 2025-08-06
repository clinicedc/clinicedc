from datetime import date

from django.db import models
from edc_consent.managers import ConsentObjectsByCdefManager, CurrentSiteByCdefManager
from edc_identifier.managers import SubjectIdentifierManager
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_model.models import BaseUuidModel
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_screening.model_mixins import ScreeningModelMixin
from edc_sites.model_mixins import SiteModelMixin
from edc_utils import get_utcnow
from edc_visit_schedule.model_mixins import OffScheduleModelMixin, OnScheduleModelMixin

from edc_crf.model_mixins import CrfModelMixin, CrfStatusModelMixin
from edc_crf.tests.consents import consent_v1


class OnSchedule(SiteModelMixin, OnScheduleModelMixin, BaseUuidModel):
    class Meta(BaseUuidModel.Meta):
        pass


class OffSchedule(SiteModelMixin, OffScheduleModelMixin, BaseUuidModel):
    class Meta(BaseUuidModel.Meta):
        pass


class SubjectScreening(ScreeningModelMixin, BaseUuidModel):
    consent_definition = consent_v1
    objects = SubjectIdentifierManager()


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


class Crf(CrfModelMixin, CrfStatusModelMixin, BaseUuidModel):
    f1 = models.CharField(max_length=50, null=True, blank=True)

    f2 = models.CharField(max_length=50, null=True, blank=True)

    f3 = models.CharField(max_length=50, null=True, blank=True)

    class Meta(CrfModelMixin.Meta, BaseUuidModel.Meta):
        pass


class CrfReportDatetimeNotRequired(CrfModelMixin, CrfStatusModelMixin, BaseUuidModel):
    report_datetime = models.DateTimeField(default=get_utcnow, null=True, blank=True)

    f1 = models.CharField(max_length=50, null=True, blank=True)

    f2 = models.CharField(max_length=50, null=True, blank=True)

    f3 = models.CharField(max_length=50, null=True, blank=True)

    def update_reference_on_save(self):
        pass

    def metadata_update(self):
        pass

    class Meta(CrfModelMixin.Meta, BaseUuidModel.Meta):
        pass
