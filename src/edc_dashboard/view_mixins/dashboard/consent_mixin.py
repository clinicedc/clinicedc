from .appointment_mixin import AppointmentMixin
from edc_consent.site_consents import site_consents
from edc_consent.exceptions import ConsentDoesNotExist
from edc_base.utils import get_utcnow


class ConsentMixin(AppointmentMixin):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._consent = None

    def consent_wrapper(self, obj):
        obj.consent_object = site_consents.get_consent(
            report_datetime=obj.consent_datetime,
            consent_model=obj._meta.label_lower,
            version=obj.version)
        return obj

    def get_utcnow(self):
        return get_utcnow()

    @property
    def consent(self):
        """Returns either the model instance or the consent_object from
        site_consents for the current period -- now -- or None."""
        if not self._consent:
            try:
                obj = self.consent_model.consent.consent_for_period(
                    self.subject_identifier, report_datetime=self.get_utcnow())
            except ConsentDoesNotExist:
                pass
            else:
                if obj:
                    self._consent = self.consent_wrapper(obj)
                else:
                    try:
                        self._consent = site_consents.get_consent(report_datetime=self.get_utcnow())
                    except ConsentDoesNotExist:
                        pass
        return self._consent

    @property
    def consents(self):
        consents = self.consent_model.objects.filter(
            subject_identifier=self.subject_identifier).order_by('version')
        consents = [
            self.consent_wrapper(obj) for obj in consents]
        return consents

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            consent=self.consent,
            consents=self.consents)
        return context
