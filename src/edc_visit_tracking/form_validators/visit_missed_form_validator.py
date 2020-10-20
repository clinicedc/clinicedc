from django.core.exceptions import ValidationError
from edc_constants.constants import NO, NOT_APPLICABLE, OTHER, YES
from edc_form_validators import FormValidator


class SubjectVisitMissedFormValidator(FormValidator):
    def clean(self):
        self.required_if(
            YES, field="contact_attempted", field_required="contact_attempts_count"
        )

        if self.cleaned_data.get("contact_made") in [NO, NOT_APPLICABLE]:
            if not self.cleaned_data.get(
                "contact_attempts_count"
            ) and self.cleaned_data.get("contact_attempts_explained"):

                raise ValidationError(
                    {"contact_attempts_explained": "This field is not required"}
                )
            if (
                self.cleaned_data.get("contact_attempts_count")
                and self.cleaned_data.get("contact_attempts_count") < 3
                and not self.cleaned_data.get("contact_attempts_explained")
            ):
                raise ValidationError(
                    {"contact_attempts_explained": "This field is required"}
                )

            if (
                self.cleaned_data.get("contact_attempts_count")
                and self.cleaned_data.get("contact_attempts_count") >= 3
                and self.cleaned_data.get("contact_attempts_explained")
            ):
                raise ValidationError(
                    {"contact_attempts_explained": "This field is not required"}
                )

        self.required_if(
            YES, field="contact_attempted", field_required="contact_last_date"
        )

        self.required_if(YES, field="contact_attempted", field_required="contact_made")

        self.m2m_required_if(YES, field="contact_made", m2m_field="missed_reasons")

        self.m2m_other_specify(
            OTHER, m2m_field="missed_reasons", field_other="missed_reasons_other"
        )
