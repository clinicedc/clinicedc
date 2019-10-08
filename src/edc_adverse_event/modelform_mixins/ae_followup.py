from django import forms
from django.conf import settings
from edc_action_item.forms import ActionItemFormMixin
from edc_constants.constants import YES, DEAD
from edc_form_validators import FormValidatorMixin, FormValidator
from edc_registration.modelform_mixins import ModelFormSubjectIdentifierMixin
from edc_reportable import SEVERITY_INCREASED_FROM_G3, GRADE5
from edc_utils.text import convert_php_dateformat


class DefaultAeFollowupFormValidator(FormValidator):
    def clean(self):

        self.applicable_if(
            SEVERITY_INCREASED_FROM_G3, field="outcome", field_applicable="ae_grade"
        )

        self.applicable_if(
            SEVERITY_INCREASED_FROM_G3, field="outcome", field_applicable="ae_grade"
        )


class AeFollowupModelFormMixin(
    FormValidatorMixin, ModelFormSubjectIdentifierMixin, ActionItemFormMixin
):

    form_validator_cls = DefaultAeFollowupFormValidator

    subject_identifier = forms.CharField(
        label="Subject Identifier",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
        help_text="(read-only)",
    )

    def clean(self):
        cleaned_data = super().clean()

        self.validate_ae_initial_outcode_date()
        self.validate_no_followup_upon_death()

        return cleaned_data

    def validate_ae_initial_outcode_date(self):
        ae_initial = self.cleaned_data.get("ae_initial")
        if not ae_initial and self.instance:
            ae_initial = self.instance.ae_initial
        outcome_date = self.cleaned_data.get("outcome_date")
        if ae_initial and outcome_date:
            if outcome_date < ae_initial.ae_start_date:
                formatted_dte = ae_initial.ae_start_date.strftime(
                    convert_php_dateformat(settings.SHORT_DATE_FORMAT)
                )
                raise forms.ValidationError(
                    {
                        "outcome_date": (
                            f"May not be before the AE start date {formatted_dte}."
                        )
                    }
                )

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
