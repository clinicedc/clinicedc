from django import forms

from edc_constants.constants import NO, YES

___all__ = ["ReviewFieldsModelFormMixin"]


class ReviewFieldsModelFormMixin:
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
