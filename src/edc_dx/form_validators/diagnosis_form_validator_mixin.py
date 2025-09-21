from django import forms
from edc_constants.constants import YES

from ..diagnoses import (
    ClinicalReviewBaselineRequired,
    Diagnoses,
    InitialReviewRequired,
    MultipleInitialReviewsExist,
)


class DiagnosisFormValidatorMixin:
    def get_diagnoses(self) -> Diagnoses:
        try:
            diagnoses = Diagnoses(
                subject_identifier=self.subject_identifier,
                report_datetime=self.report_datetime,
            )
        except ClinicalReviewBaselineRequired as e:
            raise forms.ValidationError(e)
        try:
            diagnoses.get_initial_reviews()
        except InitialReviewRequired as e:
            raise forms.ValidationError(e)
        except MultipleInitialReviewsExist as e:
            raise forms.ValidationError(e)
        return diagnoses

    def applicable_if_not_diagnosed(
        self, diagnoses=None, prefix=None, field_applicable=None, label=None
    ) -> bool:
        diagnoses = diagnoses or self.get_diagnoses()
        return self.applicable_if_true(
            diagnoses.get_dx(prefix) != YES,
            field_applicable=field_applicable,
            applicable_msg=(
                f"Patient was not previously diagnosed with {label}. Expected YES or NO."
            ),
            not_applicable_msg=f"Patient was previously diagnosed with {label}.",
        )

    def applicable_if_diagnosed(
        self, diagnoses=None, prefix=None, field_applicable=None, label=None
    ) -> bool:
        diagnoses = diagnoses or self.get_diagnoses()
        diagnosed = diagnoses.get_dx(prefix) == YES
        return self.applicable_if_true(
            diagnosed,
            field_applicable=field_applicable,
            applicable_msg=(
                f"Patient was previously diagnosed with {label}. Expected YES or NO."
            ),
            not_applicable_msg=f"Patient was not previously diagnosed with {label}.",
        )
