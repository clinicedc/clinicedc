from django import forms
from edc_action_item.forms import ActionItemFormMixin
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_form_validators import FormValidator
from edc_lab_panel.panels import fbc_panel, hba1c_panel

from edc_lab_results.form_validator_mixins import BloodResultsFormValidatorMixin

from .models import BloodResultsFbc, BloodResultsHba1c


class BloodResultsFbcFormValidator(BloodResultsFormValidatorMixin, FormValidator):
    panel = fbc_panel


class BloodResultsHba1cFormValidator(BloodResultsFormValidatorMixin, FormValidator):
    panel = hba1c_panel


class BloodResultsFbcForm(ActionItemFormMixin, CrfModelFormMixin, forms.ModelForm):

    form_validator_cls = BloodResultsFbcFormValidator

    def validate_against_consent(self):
        """Skip for tests"""
        pass

    class Meta:
        model = BloodResultsFbc
        fields = "__all__"


class BloodResultsHba1cForm(CrfModelFormMixin, forms.ModelForm):

    form_validator_cls = BloodResultsHba1cFormValidator

    def validate_against_consent(self):
        """Skip for tests"""
        pass

    class Meta:
        model = BloodResultsHba1c
        fields = "__all__"
