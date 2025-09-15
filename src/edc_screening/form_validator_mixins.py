from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from edc_consent import site_consents

from .utils import get_subject_screening_model

if TYPE_CHECKING:
    from edc_consent.consent_definition import ConsentDefinition

    from .model_mixins import ScreeningModelMixin


class SubjectScreeningFormValidatorMixin:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._subject_screening = None

    @property
    def screening_identifier(self):
        return self.cleaned_data.get("screening_identifier")

    @property
    def report_datetime(self):
        return self.cleaned_data.get("report_datetime")

    @property
    def subject_screening_model(self) -> str:
        return get_subject_screening_model()

    @property
    def subject_screening_model_cls(self) -> type[ScreeningModelMixin]:
        return django_apps.get_model(self.subject_screening_model)

    @property
    def subject_screening(self) -> ScreeningModelMixin:
        if not self._subject_screening:
            try:
                self._subject_screening = self.subject_screening_model_cls.objects.get(
                    screening_identifier=self.screening_identifier
                )
            except ObjectDoesNotExist:
                self.raise_validation_error(
                    'Complete the "Subject Screening" form before proceeding.',
                    error_code="missing_subject_screening",
                )
        return self._subject_screening

    def get_consent_definition_or_raise(self) -> ConsentDefinition:
        """Is there a single consent definition registered"""
        return site_consents.get_consent_definition(
            screening_model=self.instance._meta.label_lower,
            report_datetime=self.report_datetime,
        )
