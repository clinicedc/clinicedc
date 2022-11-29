from django import forms
from edc_constants.constants import YES
from edc_crf.crf_form_validator_mixins import CrfFormValidatorMixin
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_dx.form_validators import DiagnosisFormValidatorMixin
from edc_form_validators.form_validator import FormValidator

from edc_dx_review.form_validator_mixins import ClinicalReviewFollowupFormValidatorMixin

from ..models import ClinicalReview


class ClinicalReviewFollowupFormValidator(
    ClinicalReviewFollowupFormValidatorMixin,
    CrfFormValidatorMixin,
    DiagnosisFormValidatorMixin,
    FormValidator,
):
    def clean(self):
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
