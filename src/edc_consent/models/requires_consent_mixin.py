from django.db import models

from edc_consent.site_consents import site_consents

from ..exceptions import NotConsentedError


class RequiresConsentMixin(models.Model):

    consent_model = None

    consent_version = models.CharField(max_length=10, default='?', editable=False)

    def save(self, *args, **kwargs):
        self.consented_for_period_or_raise()
        super(RequiresConsentMixin, self).save(*args, **kwargs)

    def consented_for_period_or_raise(self, report_datetime=None, subject_identifier=None, exception_cls=None):
        exception_cls = exception_cls or NotConsentedError
        report_datetime = report_datetime or self.report_datetime
        consent = self.get_consent(report_datetime, exception_cls=exception_cls)
        if not subject_identifier:
            try:
                subject_identifier = self.subject_identifier
            except AttributeError:
                subject_identifier = self.get_subject_identifier()
        try:
            self.consent.model.objects.get(
                subject_identifier=subject_identifier,
                version=self.consent.version)
        except self.consent.model.DoesNotExist:
            raise exception_cls(
                'Cannot find a consent \'{}\' for model \'{}\' using '
                'version \'{}\' and report date \'{}\'. '.format(
                    self.consent.label_lower,
                    self._meta.verbose_name,
                    self.consent.version,
                    report_datetime.isoformat()))
        self.consent_version = consent.version

    def get_consent(self, report_datetime, exception_cls=None):
        """Returns the consent that matches the report datetime and consent model."""
        return site_consents.get_by_datetime(
            self.consent_model, report_datetime, exception_cls=exception_cls)

    class Meta:
        abstract = True
