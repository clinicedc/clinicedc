from clinicedc_constants import NO, NOT_APPLICABLE, OTHER, YES
from django import forms

from edc_crf.crf_form_validator import CrfFormValidator
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_form_validators import INVALID_ERROR

from ..models import SubjectVisitMissed


class SubjectVisitMissedFormValidator(CrfFormValidator):
    def clean(self):
        self.required_if(
            YES, field="contact_attempted", field_required="contact_attempts_count"
        )

        if self.cleaned_data.get("contact_made") in [NO, NOT_APPLICABLE]:
            if not self.cleaned_data.get("contact_attempts_count") and self.cleaned_data.get(
                "contact_attempts_explained"
            ):
                self.raise_validation_error(
                    {"contact_attempts_explained": "This field is not required"}, INVALID_ERROR
                )
            if (
                self.cleaned_data.get("contact_attempts_count")
                and self.cleaned_data.get("contact_attempts_count") < 3
                and not self.cleaned_data.get("contact_attempts_explained")
            ):
                self.raise_validation_error(
                    {"contact_attempts_explained": "This field is required"}, INVALID_ERROR
                )

            if (
                self.cleaned_data.get("contact_attempts_count")
                and self.cleaned_data.get("contact_attempts_count") >= 3
                and self.cleaned_data.get("contact_attempts_explained")
            ):
                self.raise_validation_error(
                    {"contact_attempts_explained": "This field is not required"}, INVALID_ERROR
                )

        self.required_if(YES, field="contact_attempted", field_required="contact_last_date")

        self.required_if(YES, field="contact_attempted", field_required="contact_made")

        self.m2m_required_if(YES, field="contact_made", m2m_field="missed_reasons")

        self.m2m_other_specify(
            OTHER, m2m_field="missed_reasons", field_other="missed_reasons_other"
        )


class SubjectVisitMissedForm(CrfModelFormMixin, forms.ModelForm):
    form_validator_cls = SubjectVisitMissedFormValidator

    class Meta:
        model = SubjectVisitMissed
        fields = "__all__"
