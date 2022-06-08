from typing import Any

from django import forms
from edc_constants.constants import NO, YES
from edc_screening.utils import get_subject_screening_model_cls


class ConsentModelFormMixinError(Exception):
    pass


class CleanFieldsModelformMixin:
    """A model form mixin calling the default `clean_xxxxx` django
    methods.
    """

    @property
    def subject_screening_model_cls(self):
        return get_subject_screening_model_cls()

    @property
    def subject_screening(self: Any):
        screening_identifier = self.cleaned_data.get(
            "screening_identifier"
        ) or self.initial.get("screening_identifier")
        if not screening_identifier:
            raise ConsentModelFormMixinError(
                "Unable to determine the screening identifier. "
                f"This should be part of the initial form data. Got {self.cleaned_data}"
            )
        return self.subject_screening_model_cls.objects.get(
            screening_identifier=screening_identifier
        )

    def clean_consent_reviewed(self: Any) -> str:
        consent_reviewed = self.cleaned_data.get("consent_reviewed")
        if consent_reviewed != YES:
            raise forms.ValidationError(
                "Complete this part of the informed consent process before continuing.",
                code="invalid",
            )
        return consent_reviewed

    def clean_study_questions(self: Any) -> str:
        study_questions = self.cleaned_data.get("study_questions")
        if study_questions != YES:
            raise forms.ValidationError(
                "Complete this part of the informed consent process before continuing.",
                code="invalid",
            )
        return study_questions

    def clean_assessment_score(self: Any) -> str:
        assessment_score = self.cleaned_data.get("assessment_score")
        if assessment_score != YES:
            raise forms.ValidationError(
                "Complete this part of the informed consent process before continuing.",
                code="invalid",
            )
        return assessment_score

    def clean_consent_copy(self: Any) -> str:
        consent_copy = self.cleaned_data.get("consent_copy")
        if consent_copy == NO:
            raise forms.ValidationError(
                "Complete this part of the informed consent process before continuing.",
                code="invalid",
            )
        return consent_copy

    def clean_consent_signature(self: Any) -> str:
        consent_signature = self.cleaned_data.get("consent_signature")
        if consent_signature != YES:
            raise forms.ValidationError(
                "Complete this part of the informed consent process before continuing.",
                code="invalid",
            )
        return consent_signature

    def clean_initials(self: Any) -> str:
        initials = self.cleaned_data.get("initials")
        if initials and initials != self.subject_screening.initials:
            raise forms.ValidationError(
                "Initials do not match those submitted at screening. "
                f"Expected {self.subject_screening.initials}."
            )
        return initials
