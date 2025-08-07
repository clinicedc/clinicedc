from django.db import models

from edc_consent.field_mixins import PersonalFieldsMixin
from edc_consent.managers import ConsentObjectsByCdefManager, CurrentSiteByCdefManager
from edc_consent.model_mixins import ConsentModelMixin
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierModelMixin
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_search.model_mixins import SearchSlugManager
from edc_sites.managers import CurrentSiteManager
from edc_sites.model_mixins import SiteModelMixin


class SubjectConsentManager(SearchSlugManager, models.Manager):
    def get_by_natural_key(self, subject_identifier, version):
        return self.get(subject_identifier=subject_identifier, version=version)


class SubjectConsent(
    ConsentModelMixin,
    SiteModelMixin,
    NonUniqueSubjectIdentifierModelMixin,
    PersonalFieldsMixin,
    BaseUuidModel,
):
    screening_identifier = models.CharField(
        verbose_name="Screening identifier", max_length=50, unique=True
    )

    on_site = CurrentSiteManager()

    objects = SubjectConsentManager()

    history = HistoricalRecords()

    class Meta(ConsentModelMixin.Meta):
        verbose_name = "Subject Consent"


class SubjectConsentV1(SubjectConsent):
    objects = ConsentObjectsByCdefManager()

    on_site = CurrentSiteByCdefManager()

    history = HistoricalRecords()

    class Meta(ConsentModelMixin.Meta):
        verbose_name = "Subject Consent V1"
        proxy = True


class SubjectConsentV2(SubjectConsent):
    objects = ConsentObjectsByCdefManager()

    on_site = CurrentSiteByCdefManager()

    history = HistoricalRecords()

    class Meta(ConsentModelMixin.Meta):
        verbose_name = "Subject Consent V2"
        proxy = True
