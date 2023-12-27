from __future__ import annotations

from typing import TYPE_CHECKING, Any

from edc_sites.site import sites
from edc_utils import get_uuid

from .exceptions import ConsentObjectDoesNotExist
from .site_consents import site_consents

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from edc_model_wrapper import ModelWrapper

    from .consent import Consent
    from .stubs import ConsentLikeModel


class ConsentViewMixin:

    """Declare with edc_appointment view mixin to get `appointment`."""

    consent_model_wrapper_cls = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._consent = None
        self._consents = None

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        kwargs.update(
            consent=self.consent_wrapped,
            consents=self.consents_wrapped,
            consent_object=self.consent_object,
        )
        return super().get_context_data(**kwargs)

    @property
    def consents(self) -> QuerySet[ConsentLikeModel]:
        """Returns a Queryset of consents for this subject."""
        return self.consent_object.model_cls.objects.filter(
            subject_identifier=self.subject_identifier,
            site_id__in=sites.get_site_ids_for_user(request=self.request),
        ).order_by("version")

    @property
    def consent(self) -> ConsentLikeModel | None:
        """Returns a consent model instance or None for the current period."""
        return self.consent_object.model_cls.consent.consent_for_period(
            subject_identifier=self.subject_identifier,
            report_datetime=self.report_datetime,
        )

    @property
    def empty_consent(self) -> ConsentLikeModel:
        """Returns an unsaved consent model instance.

        Override to include additional attrs to instantiate.
        """
        return self.consent_object.model_cls(
            subject_identifier=self.subject_identifier,
            consent_identifier=get_uuid(),
            version=self.consent_object.version,
        )

    @property
    def consent_object(self) -> Consent | None:
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
    def consent_wrapped(self) -> ModelWrapper:
        """Returns a wrapped consent, either saved or not,
        for the current period.
        """
        return self.consent_model_wrapper_cls(self.consent or self.empty_consent)

    @property
    def consents_wrapped(self) -> list[ModelWrapper]:
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
