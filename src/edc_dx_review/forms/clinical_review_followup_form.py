from django import forms
from edc_constants.constants import DM, HIV, HTN, NO, YES
from edc_crf.forms.crf_form_validator_mixin import CrfFormValidatorMixin
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_dx import get_diagnosis_labels, get_diagnosis_labels_prefixes
from edc_dx.form_validators import DiagnosisFormValidatorMixin
from edc_form_validators.form_validator import FormValidator
from edc_visit_schedule.utils import raise_if_baseline

from ..models import ClinicalReview


class ClinicalReviewFollowupFormValidator(
    CrfFormValidatorMixin,
    DiagnosisFormValidatorMixin,
    FormValidator,
):
    def clean(self):
        raise_if_baseline(self.cleaned_data.get("subject_visit"))
        for prefix, label in get_diagnosis_labels().items():
            self.applicable_if_not_diagnosed(
                prefix=prefix,
                field_applicable=f"{prefix}_test",
                label=label,
            )
            self.required_if(YES, field=f"{prefix}_test", field_required=f"{prefix}_test_date")
            self.required_if(YES, field=f"{prefix}_test", field_required=f"{prefix}_reason")
            self.applicable_if(YES, field=f"{prefix}_test", field_applicable=f"{prefix}_dx")

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


class ClinicalReviewFollowupForm(CrfModelFormMixin, forms.ModelForm):

    form_validator_cls = ClinicalReviewFollowupFormValidator

    class Meta:
        model = ClinicalReview
        fields = "__all__"
