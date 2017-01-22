from uuid import uuid4

from edc_base.utils import get_utcnow
from edc_consent.exceptions import ConsentDoesNotExist
from edc_consent.site_consents import site_consents


class ConsentViewMixin:

    consent_model = None
    consent_model_wrapper_class = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._consent = None
        self._consents = None
        self._consent_object = None

    def get(self, request, *args, **kwargs):
        kwargs['consent'] = self.consent
        kwargs['consents'] = self.consents
        kwargs['consent_object'] = self.consent_object
        return super().get(request, *args, **kwargs)

    def get_utcnow(self):
        return get_utcnow()

    @property
    def consent_object(self):
        """Returns a consent object or None from site_consents for the current period."""
        if not self._consent_object:
            try:
                self._consent_object = site_consents.get_consent(
                    report_datetime=self.get_utcnow())
            except ConsentDoesNotExist:
                self._consent_object = None
        return self._consent_object

    @property
    def consent(self):
        """Returns a wrapped model instance or None for the current period."""
        if not self._consent:
            consent = self.consent_model.consent.consent_for_period(
                self.subject_identifier, report_datetime=self.get_utcnow())
            if consent:
                self._consent = self.consent_model_wrapper_class(consent)
            else:
                self._consent = self.consent_model_wrapper_class(
                    self.empty_consent)
        return self._consent

    @property
    def empty_consent(self):
        """Returns an unsaved consent model instance.

        Override to include additional attrs to instantiate."""
        return self.consent_model(
            subject_identifier=self.subject_identifier,
            consent_identifier=uuid4(),
            version=self.consent_object.version)

    @property
    def consents(self):
        if not self._consents:
            consents = self.consent_model.objects.filter(
                subject_identifier=self.subject_identifier).order_by('version')
            self._consents = [
                self.consent_model_wrapper_class(obj) for obj in consents]
        return self._consents
