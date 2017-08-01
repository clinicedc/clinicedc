from django.apps import apps as django_apps

from edc_base.utils import get_utcnow, get_uuid
from edc_consent.exceptions import ConsentDoesNotExist
from edc_consent.site_consents import site_consents


class ConsentViewMixin:

    consent_model_wrapper_cls = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._consent = None
        self._consents = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            consent=self.consent_wrapped,
            consents=self.consents_wrapped,
            consent_object=self.consent_object)
        return context

    @property
    def report_datetime(self):
        report_datetime = None
        try:
            report_datetime = self.appointment.visit.report_datetime
        except AttributeError:
            try:
                report_datetime = self.appointment.appt_datetime
            except AttributeError:
                report_datetime = get_utcnow()
        return report_datetime

    @property
    def consent_object(self):
        """Returns a consent object or None from site_consents for
        the current reporting period.
        """
        default_consent_group = django_apps.get_app_config(
            'edc_consent').default_consent_group
        try:
            consent_object = site_consents.get_consent(
                report_datetime=self.report_datetime,
                consent_group=default_consent_group)
        except ConsentDoesNotExist:
            consent_object = None
        return consent_object

    @property
    def consent(self):
        """Returns a consent model instance or None for the current period.
        """
        if not self._consent:
            self._consent = self.consent_object.model.consent.consent_for_period(
                subject_identifier=self.subject_identifier, report_datetime=self.report_datetime)
        return self._consent

    @property
    def consent_wrapped(self):
        """Returns a wrapped consent, either saved or not,
        for the current period.
        """
        if self.consent:
            return self.consent_model_wrapper_cls(self.consent)
        else:
            return self.consent_model_wrapper_cls(self.empty_consent)

    @property
    def empty_consent(self):
        """Returns an unsaved consent model instance.

        Override to include additional attrs to instantiate.
        """
        return self.consent_object.model(
            subject_identifier=self.subject_identifier,
            consent_identifier=get_uuid(),
            version=self.consent_object.version)

    @property
    def consents(self):
        """Returns a Queryset of consents for this subject.
        """
        if not self._consents:
            self._consents = self.consent_object.model.objects.filter(
                subject_identifier=self.subject_identifier).order_by('version')
        return self._consents

    @property
    def consents_wrapped(self):
        """Returns a list of wrapped consents.
        """
        if self.consents:
            return [
                self.consent_model_wrapper_cls(obj) for obj in self.consents]
        return []
