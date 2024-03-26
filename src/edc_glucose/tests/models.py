from datetime import date

from django.db import models
from edc_consent.managers import ConsentObjectsByCdefManager, CurrentSiteByCdefManager
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_model.models import BaseUuidModel
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_sites.model_mixins import SiteModelMixin
from edc_utils import get_utcnow


class SubjectScreening(
    SiteModelMixin,
    NonUniqueSubjectIdentifierFieldMixin,
    BaseUuidModel,
):
    screening_identifier = models.CharField(max_length=50)

    screening_datetime = models.DateTimeField(default=get_utcnow)

    report_datetime = models.DateTimeField(default=get_utcnow)

    age_in_years = models.IntegerField(default=25)


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
