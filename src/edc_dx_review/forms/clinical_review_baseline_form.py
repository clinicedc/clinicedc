import pdb

from django import forms
from edc_constants.constants import CHOL, DM, HIV, HTN, YES
from edc_crf.forms.crf_form_validator_mixin import CrfFormValidatorMixin
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_dx import get_diagnosis_labels_prefixes
from edc_form_validators.form_validator import FormValidator
from edc_utils.forms import EstimatedDateFromAgoFormMixin
from edc_visit_schedule.utils import raise_if_not_baseline

from ..models import ClinicalReviewBaseline


class ClinicalReviewBaselineFormValidator(
    CrfFormValidatorMixin, EstimatedDateFromAgoFormMixin, FormValidator
):
    def clean(self):
        raise_if_not_baseline(self.cleaned_data.get("subject_visit"))
        if HIV.lower() in get_diagnosis_labels_prefixes():
            self.estimated_date_from_ago("hiv_test_ago")
            self.when_tested_required(cond="hiv")
        if HTN.lower() in get_diagnosis_labels_prefixes():
            self.estimated_date_from_ago("htn_test_ago")
            self.when_tested_required(cond="htn")
            self.required_if(YES, field="htn_test", field_required="htn_dx")
        if DM.lower() in get_diagnosis_labels_prefixes():
            self.estimated_date_from_ago("dm_test_ago")
            self.when_tested_required(cond="diabetes")
            self.required_if(YES, field="dm_test", field_required="dm_dx")
        if CHOL.lower() in get_diagnosis_labels_prefixes():
            self.estimated_date_from_ago("chol_test_ago")
            self.when_tested_required(cond="cholesterol")
            self.required_if(YES, field="chol_test", field_required="chol_dx")

    def when_tested_required(self, cond=None):
        if self.cleaned_data.get(f"{cond}_test") == YES:
            if not self.cleaned_data.get(f"{cond}_test_ago") and not self.cleaned_data.get(
                f"{cond}_test_date"
            ):
                raise forms.ValidationError(
                    f"{cond.title()}: When was the subject tested? Either provide an "
                    "estimated time 'ago' or provide the exact date. See below."
                )


class ClinicalReviewBaselineForm(CrfModelFormMixin, forms.ModelForm):

    form_validator_cls = ClinicalReviewBaselineFormValidator

    class Meta:
        model = ClinicalReviewBaseline
        fields = "__all__"
