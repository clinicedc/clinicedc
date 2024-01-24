from datetime import date

from django.db import models
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_model.models import BaseUuidModel
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_sites.model_mixins import SiteModelMixin
from edc_utils import get_utcnow

from edc_crf.model_mixins import CrfModelMixin, CrfStatusModelMixin


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
