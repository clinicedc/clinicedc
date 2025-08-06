from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib import messages
from django.contrib.messages import ERROR

from edc_sites import site_sites

from .. import site_consents
from ..exceptions import ConsentDefinitionDoesNotExist, NotConsentedError

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from ..consent_definition import ConsentDefinition
    from ..stubs import ConsentLikeModel


class ConsentViewMixin:
    consent_model: str | dict[str, str] = None

    """Declare with edc_appointment view mixin to get `appointment`."""

    def __init__(self, **kwargs):
        self._consent: ConsentLikeModel | None = None
        self._consents: QuerySet | None = None
        self._consent_definition: ConsentDefinition | None = None
        super().__init__(**kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Add consent_definition and consents to the dashboard."""
        # TODO: What if active on more than one schedule??
        try:
            kwargs.update(consent_definition=self.consent_definition)
        except ConsentDefinitionDoesNotExist as e:
            messages.add_message(self.request, message=str(e), level=ERROR)
        else:
            kwargs.update(consent=self.consent, consents=self.consents)
        return super().get_context_data(**kwargs)

    @property
    def consents(self) -> QuerySet[ConsentLikeModel]:
        """Returns a Queryset of consents for this subject."""
        if not self._consents:
            self._consents = site_consents.get_consents(
                self.subject_identifier, site_id=self.request.site.id
            )
        return self._consents

    @property
    def consent(self) -> ConsentLikeModel | None:
        """Returns a consent model instance or None for the current
        period.
        """
        if not self._consent:
            try:
                self._consent = site_consents.get_consent_or_raise(
                    subject_identifier=self.subject_identifier,
                    report_datetime=self.report_datetime,
                    site_id=self.request.site.id,
                )
            except NotConsentedError as e:
                messages.add_message(self.request, message=str(e), level=ERROR)
        return self._consent

    @property
    def consent_definition(self) -> ConsentDefinition:
        """Returns a ConsentDefinition from the schedule for the
        current reporting period.
        """
        if not self._consent_definition:
            if self.current_schedule:
                self._consent_definition = self.current_schedule.get_consent_definition(
                    report_datetime=self.report_datetime,
                    site=site_sites.get(self.request.site.id),
                )
            elif self.appointment:
                self._consent_definition = self.appointment.schedule.get_consent_definition(
                    report_datetime=self.appointment.appt_datetime,
                    site=site_sites.get(self.appointment.site.id),
                )
        return self._consent_definition
