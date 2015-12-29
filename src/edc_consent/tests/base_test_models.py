from django.db import models
from django.utils import timezone

from edc_base.model.models import BaseUuidModel
from edc_base.audit_trail import AuditTrail
from edc_consent.forms.base_consent_form import BaseConsentForm
from edc_consent.models import BaseConsent, RequiresConsentMixin, BaseSpecimenConsent
from edc_consent.models.fields import (
    IdentityFieldsMixin, SampleCollectionFieldsMixin, PersonalFieldsMixin,
    VulnerabilityFieldsMixin, SiteFieldsMixin)
from edc_quota.client.models import QuotaMixin, QuotaManager


class ConsentQuotaMixin(QuotaMixin):

    QUOTA_REACHED_MESSAGE = 'Maximum number of subjects has been reached or exceeded for {}. Got {} >= {}.'

    class Meta:
        abstract = True


class TestConsentModel(
        BaseConsent, ConsentQuotaMixin, IdentityFieldsMixin, SampleCollectionFieldsMixin,
        SiteFieldsMixin, PersonalFieldsMixin, VulnerabilityFieldsMixin, BaseUuidModel):

    objects = models.Manager()

    history = AuditTrail()

    quota = QuotaManager()

    class Meta:
        app_label = 'edc_consent'
        unique_together = (
            ('subject_identifier', 'version'),
            ('identity', 'version'),
            ('first_name', 'dob', 'initials', 'version'))


class TestConsentModelProxy(TestConsentModel):

    MAX_AGE_OF_CONSENT = 120
    GENDER_OF_CONSENT = ['M']

    class Meta:
        app_label = 'edc_consent'  # required!
        proxy = True


class TestModel(RequiresConsentMixin, BaseUuidModel):

    consent_model = TestConsentModel

    subject_identifier = models.CharField(max_length=10)

    report_datetime = models.DateTimeField(default=timezone.now)

    field1 = models.CharField(max_length=10)

    objects = models.Manager()

    history = AuditTrail()

    class Meta:
        app_label = 'edc_consent'
        verbose_name = 'Test Model'


class Visit(models.Model):

    subject_identifier = models.CharField(max_length=10)

    report_datetime = models.DateTimeField(default=timezone.now)

    objects = models.Manager()

    class Meta:
        app_label = 'edc_consent'
        verbose_name = 'Visit'


class TestScheduledModel(RequiresConsentMixin, models.Model):

    consent_model = TestConsentModel

    visit = models.ForeignKey(Visit)

    report_datetime = models.DateTimeField(default=timezone.now)

    objects = models.Manager()

    def get_subject_identifier(self):
        return self.visit.subject_identifier

    class Meta:
        app_label = 'edc_consent'


class ConsentForm(BaseConsentForm):

    class Meta:
        model = TestConsentModel
        fields = '__all__'


class ConsentModelProxyForm(BaseConsentForm):

    class Meta:
        model = TestConsentModelProxy
        fields = '__all__'


class TestSpecimenConsent(BaseSpecimenConsent):

    class Meta:
        app_label = 'edc_consent'
