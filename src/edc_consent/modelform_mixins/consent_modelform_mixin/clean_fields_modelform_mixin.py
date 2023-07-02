from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms
from edc_constants.constants import NO, YES
from edc_screening.utils import (
    get_subject_screening_model_cls,
    get_subject_screening_or_raise,
)

if TYPE_CHECKING:
    from edc_screening.model_mixins import ScreeningModelMixin


class ConsentModelFormMixinError(Exception):
    pass


class CleanFieldsModelformMixin:
    """A model form mixin calling the default `clean_xxxxx` django
    methods.
    """

    @property
    def subject_screening_model_cls(self) -> ScreeningModelMixin:
        return get_subject_screening_model_cls()

    @property
    def subject_screening(self):
        screening_identifier = self.cleaned_data.get(
            "screening_identifier"
        ) or self.initial.get("screening_identifier")
        if not screening_identifier:
            raise forms.ValidationError(
                "Unable to determine the screening identifier. "
                f"This should be part of the initial form data. Got {self.cleaned_data}"
            )
        # try:
        #     subject_screening = self.subject_screening_model_cls.objects.get(
        #         screening_identifier=screening_identifier
        #     )
        # except ObjectDoesNotExist:
        #     raise forms.ValidationError(
        #         "Unable to find screening form. Invalid screening identifier. "
        #         f"Got `{screening_identifier}`"
        #     )
        return get_subject_screening_or_raise(screening_identifier, is_modelform=True)

    def clean_consent_reviewed(self) -> str:
        consent_reviewed = self.cleaned_data.get("consent_reviewed")
        if consent_reviewed != YES:
            raise forms.ValidationError(
                "Complete this part of the informed consent process before continuing.",
                code="invalid",
            )
        return consent_reviewed

    def clean_study_questions(self) -> str:
        study_questions = self.cleaned_data.get("study_questions")
        if study_questions != YES:
            raise forms.ValidationError(
                "Complete this part of the informed consent process before continuing.",
                code="invalid",
            )
        return study_questions

    def clean_assessment_score(self) -> str:
        assessment_score = self.cleaned_data.get("assessment_score")
        if assessment_score != YES:
            raise forms.ValidationError(
                "Complete this part of the informed consent process before continuing.",
                code="invalid",
            )
        return assessment_score

    def clean_consent_copy(self) -> str:
        consent_copy = self.cleaned_data.get("consent_copy")
        if consent_copy == NO:
            raise forms.ValidationError(
                "Complete this part of the informed consent process before continuing.",
                code="invalid",
            )
        return consent_copy

    def clean_consent_signature(self) -> str:
        consent_signature = self.cleaned_data.get("consent_signature")
        if consent_signature != YES:
            raise forms.ValidationError(
                "Complete this part of the informed consent process before continuing.",
                code="invalid",
            )
        return consent_signature

    def clean_initials(self) -> str:
        initials = self.cleaned_data.get("initials")
        if initials and initials != self.subject_screening.initials:
            raise forms.ValidationError(
                "Initials do not match those submitted at screening. "
                f"Expected {self.subject_screening.initials}."
            )
        return initials
