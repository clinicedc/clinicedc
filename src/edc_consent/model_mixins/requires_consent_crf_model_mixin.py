from ..requires_consent import RequiresConsent
from .requires_consent_fields_mixin import RequiresConsentFieldsMixin


class RequiresConsentCrfModelMixin(RequiresConsentFieldsMixin):

    """Requires a CRF model to check for a valid consent before
    allowing to save.
    """

    requires_consent_cls = RequiresConsent

    def save(self, *args, **kwargs):
        schedule = self.visit.appointment.schedule
        requires_consent = self.requires_consent_cls(
            model=self._meta.label_lower,
            subject_identifier=self.subject_identifier,
            report_datetime=self.report_datetime,
            consent_model=schedule.consent_model)
        self.consent_version = requires_consent.version
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
