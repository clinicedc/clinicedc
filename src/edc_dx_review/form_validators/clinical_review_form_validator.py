from django import forms
from edc_constants.constants import NO, YES
from edc_dx.form_validators import DiagnosisFormValidatorMixin
from edc_form_validators.form_validator import FormValidator

from .mixins import CrfFormValidatorMixin, CrfModelFormMixin


class ClinicalReviewFormValidator(
    CrfFormValidatorMixin,
    DiagnosisFormValidatorMixin,
    FormValidator,
):
    def clean(self):
        diagnoses = self.get_diagnoses()

        # htn
        self.applicable_if_not_diagnosed(
            diagnoses=diagnoses,
            field_dx="htn_dx",
            field_applicable="htn_test",
            label="hypertension",
        )
        self.required_if(YES, field="htn_test", field_required="htn_test_date")
        self.required_if(YES, field="htn_test", field_required="htn_reason")
        self.applicable_if(YES, field="htn_test", field_applicable="htn_dx")

        # diabetes
        self.applicable_if_not_diagnosed(
            diagnoses=diagnoses,
            field_dx="dm_dx",
            field_applicable="dm_test",
            label="diabetes",
        )
        self.required_if(YES, field="dm_test", field_required="dm_test_date")
        self.required_if(YES, field="dm_test", field_required="dm_reason")
        self.applicable_if(YES, field="dm_test", field_applicable="dm_dx")

        # hiv
        self.applicable_if_not_diagnosed(
            diagnoses=diagnoses,
            field_dx="hiv_dx",
            field_applicable="hiv_test",
            label="HIV",
        )
        self.required_if(YES, field="hiv_test", field_required="hiv_test_date")
        self.required_if(YES, field="hiv_test", field_required="hiv_reason")
        self.applicable_if(YES, field="hiv_test", field_applicable="hiv_dx")

        self.required_if(
            YES,
            field="health_insurance",
            field_required="health_insurance_monthly_pay",
            field_required_evaluate_as_int=True,
        )
        self.required_if(
            YES,
            field="patient_club",
            field_required="patient_club_monthly_pay",
            field_required_evaluate_as_int=True,
        )

    def raise_if_dx_and_applicable(self, clinic, cond):
        if self.subject_screening.clinic_type in [clinic] and self.cleaned_data.get(
            f"{cond}_test"
        ) in [YES, NO]:
            raise forms.ValidationError(
                {
                    f"{cond}_test": (
                        f"Not applicable. Patient was recruited from the {cond.title} clinic."
                    ),
                }
            )
