from django import forms
from edc_crf.modelform_mixins import CrfModelFormMixin

from ..form_validators import ClinicalReviewFormValidator
from ..models import ClinicalReview


class ClinicalReviewForm(CrfModelFormMixin, forms.ModelForm):

    form_validator_cls = ClinicalReviewFormValidator

    class Meta:
        model = ClinicalReview
        fields = "__all__"
