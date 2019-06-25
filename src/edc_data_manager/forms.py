from django import forms
from edc_action_item.forms.action_item_form_mixin import ActionItemFormMixin
from edc_constants.constants import RESOLVED, OPEN, FEEDBACK, HIGH_PRIORITY, NEW
from edc_form_validators import FormValidator, FormValidatorMixin

from .models import DataQuery
from .constants import RESOLVED_WITH_ACTION


class DataQueryFormValidator(FormValidator):
    def clean(self):

        self.required_if(
            HIGH_PRIORITY,
            field="query_priority",
            field_required="recipients",
            inverse=False,
        )

        # Site
        self.required_if(
            RESOLVED,
            field="site_response_status",
            field_required="site_resolved_datetime",
        )
        self.required_if(
            OPEN,
            FEEDBACK,
            RESOLVED,
            field="site_response_status",
            field_required="site_response_text",
        )

        if self.cleaned_data.get("site_response_status") in [
            NEW,
            OPEN,
            FEEDBACK,
        ] and self.cleaned_data.get("status") in [RESOLVED, RESOLVED_WITH_ACTION]:
            raise forms.ValidationError(
                {"status": "Invalid: Site response is not resolved."}
            )

        # TCC
        self.required_if(
            RESOLVED,
            RESOLVED_WITH_ACTION,
            field="status",
            field_required="resolved_datetime",
        )
        self.required_if(
            RESOLVED, RESOLVED_WITH_ACTION, field="status", field_required="tcc_user"
        )
        self.required_if(
            RESOLVED_WITH_ACTION, field="status", field_required="plan_of_action"
        )


class DataQueryForm(FormValidatorMixin, ActionItemFormMixin, forms.ModelForm):

    form_validator_cls = DataQueryFormValidator

    class Meta:
        model = DataQuery
        fields = "__all__"
