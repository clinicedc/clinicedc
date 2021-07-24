from django import forms
from edc_constants.constants import NEVER, OTHER


class MedicationAdherenceFormValidatorMixin:
    def clean(self):
        self.confirm_visual_scores_match()
        self.require_m2m_if_missed_any_pills()
        self.missed_pill_reason_other_specify()

    def confirm_visual_scores_match(self):
        confirmed = self.cleaned_data.get("visual_score_confirmed")
        if confirmed is not None:
            if int(self.cleaned_data.get("visual_score_slider", "0")) != confirmed:
                raise forms.ValidationError(
                    {"visual_score_confirmed": "Does not match visual score above."}
                )

    def require_m2m_if_missed_any_pills(self):
        if self.cleaned_data.get("last_missed_pill"):
            if self.cleaned_data.get("last_missed_pill") == NEVER:
                self.m2m_not_required("missed_pill_reason")
            else:
                self.m2m_required("missed_pill_reason")

    def missed_pill_reason_other_specify(self):
        self.m2m_other_specify(
            OTHER,
            m2m_field="missed_pill_reason",
            field_other="other_missed_pill_reason",
        )
