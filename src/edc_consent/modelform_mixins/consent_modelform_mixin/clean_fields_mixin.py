from typing import Any

from django import forms
from edc_constants.constants import NO, YES


class CleanFieldsMixin:
    """A model form mixin calling the default `clean_xxxxx` django
    methods.
    """

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

    def clean_gender_of_consent(self: Any) -> str:
        """Validates gender is a gender of consent."""
        gender = self.cleaned_data.get("gender")
        if gender not in self.consent_config.gender:
            raise forms.ValidationError(
                "Gender of consent can only be '%(gender_of_consent)s'. " "Got '%(gender)s'.",
                params={
                    "gender_of_consent": "' or '".join(self.consent_config.gender),
                    "gender": gender,
                },
                code="invalid",
            )
        return gender
