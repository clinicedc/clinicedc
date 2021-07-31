from django import forms
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_dx_review.forms.clinical_review_baseline_form import (
    ClinicalReviewBaselineFormValidator,
)
from edc_dx_review.models import ClinicalReviewBaseline


class ClinicalReviewBaselineForm(CrfModelFormMixin, forms.ModelForm):

    form_validator_cls = ClinicalReviewBaselineFormValidator

    def validate_against_consent(self):
        """Skip for tests"""
        pass

    class Meta:
        model = ClinicalReviewBaseline
        fields = "__all__"
