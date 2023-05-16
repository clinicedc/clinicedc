from edc_constants.constants import YES

from ...form_validators import StudyMedicationFormValidator


class StudyMedicationModelFormMixin:
    form_validator_cls = StudyMedicationFormValidator

    def clean(self):
        self.update_refill_end_datetime()
        return super().clean()

    def update_refill_end_datetime(self):
        if (
            not self.cleaned_data.get("refill_end_datetime")
            and self.cleaned_data.get("refill_to_next_visit") == YES
        ):
            if next_appt := self.related_visit.appointment.relative_next:
                self.cleaned_data["refill_end_datetime"] = next_appt.appt_datetime
