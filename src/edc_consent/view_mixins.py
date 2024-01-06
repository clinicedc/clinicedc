from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib.messages import ERROR
from edc_model_admin.utils import add_to_messages_once
from edc_sites.site import sites
from edc_utils import get_uuid

from .exceptions import ConsentDefinitionDoesNotExist
from .site_consents import SiteConsentError, site_consents

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from edc_model_wrapper import ModelWrapper

    from .consent_definition import ConsentDefinition
    from .stubs import ConsentLikeModel


class ConsentViewMixin:

    """Declare with edc_appointment view mixin to get `appointment`."""

    consent_model_wrapper_cls = None

    def __init__(self, **kwargs):
        self._consent: ConsentLikeModel | None = None
        self._consents: QuerySet | None = None
        self._consent_definition: ConsentDefinition | None = None
        self._unsaved_consent: ConsentLikeModel | None = None
        self._consent_wrapped: ModelWrapper | None = None
        self._consents_wrapped: list[ModelWrapper] = []
        super().__init__(**kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        if self.consent_definition:
            kwargs.update(
                consent=self.consent_wrapped,
                consents=self.consents_wrapped,
                consent_definition=self.consent_definition,
            )
        return super().get_context_data(**kwargs)

    @property
    def consents(self) -> QuerySet[ConsentLikeModel]:
        """Returns a Queryset of consents for this subject."""
        if not self._consents:
            self._consents = self.consent_definition.model_cls.objects.filter(
                subject_identifier=self.subject_identifier,
                site_id__in=sites.get_site_ids_for_user(request=self.request),
            ).order_by("version")
        return self._consents

    @property
    def consent(self) -> ConsentLikeModel | None:
        """Returns a consent model instance or None for the current period."""
        if not self._consent:
            if self.consent_definition:
                self._consent = self.consent_definition.get_consent_for(
                    subject_identifier=self.subject_identifier,
                    report_datetime=self.report_datetime,
                )
        return self._consent

    @property
    def unsaved_consent(self) -> ConsentLikeModel | None:
        """Returns an unsaved consent model instance.

        Override to include additional attrs to instantiate.
        """
        if not self._unsaved_consent:
            if self.consent_definition:
                self._unsaved_consent = self.consent_definition.model_cls(
                    subject_identifier=self.subject_identifier,
                    consent_identifier=get_uuid(),
                    version=self.consent_definition.version,
                )
        return self._unsaved_consent

    @property
    def consent_definition(self) -> ConsentDefinition | None:
        """Returns a ConsentDefinition or None
        from site_consents for the current reporting period.
        """
        if not self._consent_definition:
            try:
                self._consent_definition = site_consents.get_consent_definition(
                    model=self.consent_model_wrapper_cls.model,
                    report_datetime=self.report_datetime,
                )
            except ConsentDefinitionDoesNotExist:
                pass
            except SiteConsentError as e:
                add_to_messages_once(str(e), request=self.request, level=ERROR)
        return self._consent_definition

    @property
    def consent_wrapped(self) -> ModelWrapper | None:
        """Returns a wrapped consent, either saved or not,
        for the current period.
        """
        if not self._consent_wrapped:
            if self.consent or self.unsaved_consent:
                self._consent_wrapped = self.consent_model_wrapper_cls(
                    self.consent or self.unsaved_consent
                )
        return self._consent_wrapped

    @property
    def consents_wrapped(self) -> list[ModelWrapper]:
        """Returns a list of wrapped consents that this user
        has permissions to access.
        """
        if not self._consents_wrapped:
            for obj in self.consents:
                perm_list = []
                for code in ["add", "change", "view"]:
                    perm_list.append(
                        f'{obj._meta.app_label}.{code}_{obj._meta.label_lower.split(".")[1]}'
                    )
                if self.request.user.has_perms(perm_list):
                    self._consents_wrapped.append(self.consent_model_wrapper_cls(obj))
        return self._consents_wrapped
