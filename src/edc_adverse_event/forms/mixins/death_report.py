from django import forms
from edc_action_item.forms import ActionItemFormMixin
from edc_form_validators import FormValidatorMixin
from edc_sites.forms import SiteModelFormMixin

from edc_adverse_event.form_validators import DeathReportFormValidator


class DeathReportModelFormMixin(SiteModelFormMixin, ActionItemFormMixin, FormValidatorMixin):

    form_validator_cls = DeathReportFormValidator

    subject_identifier = forms.CharField(
        label="Subject identifier",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )
