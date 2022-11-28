from django import forms
from edc_crf.crf_form_validator_mixins import CrfFormValidatorMixin
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_form_validators.form_validator import FormValidator

from ..form_validator_mixins import ClinicalReviewBaselineFormValidatorMixin
from ..models import ClinicalReviewBaseline


class ClinicalReviewBaselineFormValidator(
    ClinicalReviewBaselineFormValidatorMixin, CrfFormValidatorMixin, FormValidator
):
    pass


class ClinicalReviewBaselineForm(CrfModelFormMixin, forms.ModelForm):

    form_validator_cls = ClinicalReviewBaselineFormValidator

    class Meta:
        model = ClinicalReviewBaseline
        fields = "__all__"
