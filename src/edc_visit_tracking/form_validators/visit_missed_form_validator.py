from edc_constants.constants import ALIVE, NO, OTHER, UNKNOWN, YES
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
        contact_attempts_count = (
            0
            if self.cleaned_data.get("contact_attempts_count") is None
            else self.cleaned_data.get("contact_attempts_count")
        )
        cond = (
            self.cleaned_data.get("contact_made") == NO and contact_attempts_count < 3
        )
        self.required_if_true(
            cond, field_required="contact_attempts_explained",
        )

        self.required_if(
            YES, field="contact_attempted", field_required="contact_last_date"
        )

        self.m2m_required_if(YES, field="contact_made", m2m_field="missed_reasons")

        self.m2m_other_specify(
            OTHER, m2m_field="missed_reasons", field_other="missed_reasons_other"
        )
        self.applicable_if(
            ALIVE, UNKNOWN, field="survival_status", field_applicable="ltfu"
        )
