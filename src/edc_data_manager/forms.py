from django import forms
from edc_action_item.forms.action_item_form_mixin import ActionItemFormMixin
from edc_form_validators.form_validator import FormValidator
from edc_form_validators.form_validator_mixin import FormValidatorMixin

from .models import DataQuery
from edc_constants.constants import RESOLVED, OPEN, FEEDBACK
from .constants import RESOLVED_WITH_ACTION


class DataQueryFormValidator(FormValidator):
    def clean(self):

        # Site
        self.required_if(RESOLVED,
                         field="site_response_status",
                         field_required="site_resolved_datetime")
        self.required_if(OPEN, FEEDBACK, RESOLVED,
                         field="site_response_status",
                         field_required="site_response_text")

        # TCC
        self.required_if(RESOLVED, RESOLVED_WITH_ACTION,
                         field="status", field_required="resolved_datetime")
        self.required_if(RESOLVED, RESOLVED_WITH_ACTION,
                         field="status", field_required="resolved_user")
        self.required_if(RESOLVED_WITH_ACTION,
                         field="status", field_required="plan_of_action")


class DataQueryForm(FormValidatorMixin, ActionItemFormMixin, forms.ModelForm):

    form_validator_cls = DataQueryFormValidator

    class Meta:
        model = DataQuery
        fields = "__all__"
