from edc_constants.constants import DEAD, OTHER, YES
from edc_form_validators import FormValidator


class VisitMissedFormValidator(FormValidator):
    def clean(self):

        self.applicable_if(
            YES, field="contact_attempted", field_applicable="contact_made"
        )
        self.required_if(
            YES,
            field="contact_attempted",
            field_required="contact_attempts_count",
            field_required_evaluate_as_int=True,
        )
        if self.cleaned_data.get("contact_attempts_count") is not None:
            self.required_if_true(
                self.cleaned_data.get("contact_attempts_count") < 3,
                field_required="contact_attempts_explained",
            )

        self.required_if(
            YES, field="contact_attempted", field_required="contact_last_date"
        )

        self.m2m_required_if(YES, field="contact_made", m2m_field="missed_reasons")

        self.m2m_other_specify(
            OTHER, m2m_field="missed_reasons", field_other="missed_reasons_other"
        )
        self.not_applicable_if(DEAD, field="survival_status", field_applicable="ltfu")
