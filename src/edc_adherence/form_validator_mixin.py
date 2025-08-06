from typing import Any

from django import forms
from edc_constants.constants import NEVER, OTHER, YES


class MedicationAdherenceFormValidatorMixin:
    def clean(self: Any):
        # super()._clean()  # noqa
        self.confirm_visual_scores_match()
        self.required_if(
            YES,
            field="pill_count_performed",
            field_required="pill_count",
            field_required_evaluate_as_int=True,
        )
        self.require_m2m_if_missed_any_pills()
        self.missed_pill_reason_other_specify()

    def confirm_visual_scores_match(self: Any) -> None:
        confirmed = self.cleaned_data.get("visual_score_confirmed")
        if confirmed is not None:
            if int(self.cleaned_data.get("visual_score_slider", "0")) != confirmed:
                raise forms.ValidationError(
                    {"visual_score_confirmed": "Does not match visual score above."}
                )

    def require_m2m_if_missed_any_pills(self: Any) -> None:
        if self.cleaned_data.get("last_missed_pill"):
            if self.cleaned_data.get("last_missed_pill") == NEVER:
                self.m2m_not_required("missed_pill_reason")
            else:
                self.m2m_required("missed_pill_reason")

    def missed_pill_reason_other_specify(self: Any) -> None:
        self.m2m_other_specify(
            OTHER,
            m2m_field="missed_pill_reason",
            field_other="other_missed_pill_reason",
        )
