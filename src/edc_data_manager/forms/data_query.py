from django import forms
from edc_action_item.forms.action_item_form_mixin import ActionItemFormMixin
from edc_constants.constants import RESOLVED, OPEN, FEEDBACK, HIGH_PRIORITY, NEW, CLOSED
from edc_form_validators import FormValidator, FormValidatorMixin

from ..models import DataQuery
from ..constants import CLOSED_WITH_ACTION


class DataQueryFormValidator(FormValidator):
    def clean(self):

        models = list(
            set([obj.model for obj in self.cleaned_data.get("data_dictionaries")])
        )
        if len(models) > 1:
            raise forms.ValidationError(
                {"data_dictionaries": "Invalid. Select questions from one CRF only"}
            )

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
        ] and self.cleaned_data.get("status") in [CLOSED, CLOSED_WITH_ACTION]:
            raise forms.ValidationError(
                {"status": "Invalid: Site response is not resolved."}
            )

        # DM
        self.required_if(
            CLOSED,
            CLOSED_WITH_ACTION,
            field="status",
            field_required="resolved_datetime",
        )
        self.required_if(
            CLOSED, CLOSED_WITH_ACTION, field="status", field_required="dm_user"
        )
        self.required_if(
            CLOSED_WITH_ACTION,
            field="status",
            field_required="plan_of_action",
            inverse=False,
        )


class DataQueryForm(FormValidatorMixin, ActionItemFormMixin, forms.ModelForm):

    form_validator_cls = DataQueryFormValidator

    class Meta:
        model = DataQuery
        fields = "__all__"
