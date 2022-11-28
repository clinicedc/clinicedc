from edc_constants.constants import YES
from edc_dx import get_diagnosis_labels
from edc_visit_schedule.utils import raise_if_baseline


class ClinicalReviewFollowupFormValidatorMixin:
    def _clean(self):
        raise_if_baseline(self.cleaned_data.get("subject_visit"))
        for prefix, label in get_diagnosis_labels().items():
            cond = prefix.lower()
            self.applicable_if_not_diagnosed(
                prefix=cond,
                field_applicable=f"{cond}_test",
                label=label,
            )
            self.required_if(YES, field=f"{cond}_test", field_required=f"{cond}_test_date")
            # TODO: m2m_required_if???
            self.required_if(YES, field=f"{cond}_test", field_required=f"{cond}_reason")
            self.applicable_if(YES, field=f"{cond}_test", field_applicable=f"{cond}_dx")
