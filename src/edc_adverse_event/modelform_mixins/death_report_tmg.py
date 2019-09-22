from django import forms
from edc_action_item.forms import ActionItemFormMixin
from edc_constants.constants import OTHER, CLOSED, NO, YES
from edc_form_validators import FormValidator
from edc_form_validators import FormValidatorMixin
from edc_sites.forms import SiteModelFormMixin


class DefaultDeathReportTmgFormValidator(FormValidator):
    def clean(self):

        self.required_if(
            CLOSED,
            field="report_status",
            field_required="cause_of_death",
            inverse=False,
        )

        self.validate_other_specify(
            field="cause_of_death",
            other_specify_field="cause_of_death_other",
            other_stored_value=OTHER,
        )

        if self.cause_of_death:
            if (
                self.cleaned_data.get("cause_of_death_agreed") == NO
                and self.death_report_cause_of_death == self.tmg_cause_of_death
            ):
                raise forms.ValidationError(
                    {
                        "cause_of_death_agreed": (
                            "Cause of death reported by the study doctor matches "
                            "your assessment."
                        )
                    }
                )
            elif (
                self.cleaned_data.get("cause_of_death_agreed") == YES
                and self.cause_of_death != self.tmg_cause_of_death
            ):
                raise forms.ValidationError(
                    {
                        "cause_of_death_agreed": (
                            "Cause of death reported by the study doctor "
                            "does not match your assessment."
                        )
                    }
                )

        self.required_if(
            CLOSED,
            field="report_status",
            field_required="cause_of_death_agreed",
            inverse=False,
        )

        self.required_if(
            NO, field="cause_of_death_agreed", field_required="narrative", inverse=False
        )

        self.required_if(
            CLOSED, field="report_status", field_required="report_closed_datetime"
        )

    @property
    def cause_of_death(self):
        try:
            return self.cleaned_data.get("cause_of_death").short_name
        except AttributeError:
            return None

    @property
    def death_report_cause_of_death(self):
        death_report = (
            self.cleaned_data.get("death_report") or self.instance.death_report
        )
        if death_report.cause_of_death.short_name == OTHER:
            death_report_cause_of_death = (
                (death_report.cause_of_death_other or "").strip().lower()
            )
        else:
            death_report_cause_of_death = death_report.cause_of_death.short_name
        return death_report_cause_of_death

    @property
    def tmg_cause_of_death(self):
        if self.cause_of_death == OTHER:
            tmg_cause_of_death = (
                (self.cleaned_data.get("cause_of_death_other") or "").strip().lower()
            )
        else:
            tmg_cause_of_death = self.cause_of_death
        return tmg_cause_of_death


class DeathReportTmgModelFormMixin(
    SiteModelFormMixin, FormValidatorMixin, ActionItemFormMixin
):

    form_validator_cls = DefaultDeathReportTmgFormValidator

    subject_identifier = forms.CharField(
        label="Subject identifier",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )
