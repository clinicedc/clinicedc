from django.views.generic.base import ContextMixin
from edc_utils import get_utcnow, get_uuid

from .exceptions import ConsentObjectDoesNotExist
from .site_consents import site_consents


class ConsentViewMixin(ContextMixin):

    """Declare with edc_appointment view mixin to get `appointment`."""

    consent_model_wrapper_cls = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._consent = None
        self._consents = None

    # @property
    # @abstractmethod
    # def appointment(self):
    #     pass
    #
    # @property
    # @abstractmethod
    # def subject_identifier(self):
    #     pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            consent=self.consent_wrapped,
            consents=self.consents_wrapped,
            consent_object=self.consent_object,
        )
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
                pass
        return report_datetime or get_utcnow()

    @property
    def consent_object(self):
        """Returns a consent_config object or None
        from site_consents for the current reporting period.
        """
        try:
            consent_object = site_consents.get_consent_for_period(
                model=self.consent_model_wrapper_cls.model,
                report_datetime=self.report_datetime,
            )
        except ConsentObjectDoesNotExist:
            consent_object = None
        return consent_object

    @property
    def consent(self):
        """Returns a consent model instance or None for the current period."""
        return self.consent_object.model_cls.consent.consent_for_period(
            subject_identifier=self.subject_identifier,
            report_datetime=self.report_datetime,
        )

    @property
    def consent_wrapped(self):
        """Returns a wrapped consent, either saved or not,
        for the current period.
        """
        return self.consent_model_wrapper_cls(self.consent or self.empty_consent)

    @property
    def empty_consent(self):
        """Returns an unsaved consent model instance.

        Override to include additional attrs to instantiate.
        """
        return self.consent_object.model_cls(
            subject_identifier=self.subject_identifier,
            consent_identifier=get_uuid(),
            version=self.consent_object.version,
        )

    @property
    def consents(self):
        """Returns a Queryset of consents for this subject."""
        return self.consent_object.model_cls.objects.filter(
            subject_identifier=self.subject_identifier
        ).order_by("version")

    @property
    def consents_wrapped(self):
        """Returns a list of wrapped consents that this user
        has permissions to access.
        """
        consents_wrapped = []
        for obj in self.consents:
            perm_list = []
            for code in ["add", "change", "view"]:
                perm_list.append(
                    f'{obj._meta.app_label}.{code}_{obj._meta.label_lower.split(".")[1]}'
                )
            if self.request.user.has_perms(perm_list):
                consents_wrapped.append(self.consent_model_wrapper_cls(obj))
        return consents_wrapped
