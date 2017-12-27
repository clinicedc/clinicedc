from django.db.models import options

from ..requires_consent import RequiresConsent
from .requires_consent_fields_mixin import RequiresConsentFieldsMixin

if 'consent_model' not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = (options.DEFAULT_NAMES
                             + ('consent_model', ))

if 'consent_group' not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = (options.DEFAULT_NAMES
                             + ('consent_group', ))


class RequiresConsentNonCrfModelMixin(RequiresConsentFieldsMixin):

    """Requires a model to check for and set a valid
    consent version before allowing to save.

    Requires attrs subject_identfier, schedule, report_datetime.
    """

    requires_consent_cls = RequiresConsent

    def save(self, *args, **kwargs):
        if not self.consent_model:
            try:
                self.consent_model = self.schedule.consent_model
            except AttributeError:
                self.consent_model = self._meta.consent_model
        requires_consent = self.requires_consent_cls(
            model=self._meta.label_lower,
            subject_identifier=self.subject_identifier,
            report_datetime=self.report_datetime,
            consent_model=self.consent_model)
        self.consent_version = requires_consent.version
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        consent_model = None
        consent_group = None
