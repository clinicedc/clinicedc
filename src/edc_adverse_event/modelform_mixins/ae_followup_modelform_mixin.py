from django import forms
from edc_constants.constants import DEAD, YES
from edc_reportable import GRADE5

from ..form_validators import AeFollowupFormValidator
from ..utils import validate_ae_initial_outcome_date
from .ae_modelform_mixin import AeModelFormMixin


class AeFollowupModelFormMixin(AeModelFormMixin):
    form_validator_cls = AeFollowupFormValidator

    def clean(self):
        cleaned_data = super().clean()
        validate_ae_initial_outcome_date(self)
        self.validate_no_followup_upon_death()
        return cleaned_data

    def validate_no_followup_upon_death(self):
        if self.cleaned_data.get("followup") == YES:
            if (
                self.cleaned_data.get("ae_grade") == GRADE5
                or self.cleaned_data.get("outcome") == DEAD
            ):
                raise forms.ValidationError(
                    {
                        "followup": (
                            "Expected No. Submit a death report when the "
                            "severity increases to grade 5."
                        )
                    }
                )

    class Meta:
        help_text = {"subject_identifier": "(read-only)", "action_identifier": "(read-only)"}
        widgets = {
            "subject_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
            "action_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }
