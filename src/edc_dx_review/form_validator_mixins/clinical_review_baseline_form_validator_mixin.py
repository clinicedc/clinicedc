from edc_constants.constants import YES
from edc_dx import get_diagnosis_labels, get_diagnosis_labels_prefixes
from edc_model import estimated_date_from_ago
from edc_visit_schedule.utils import raise_if_not_baseline

MISSING_TEST_DATE = "MISSING_TEST_DATE"


class ClinicalReviewBaselineFormValidatorMixin:
    def _clean(self):
        raise_if_not_baseline(self.cleaned_data.get("subject_visit"))

        for prefix in get_diagnosis_labels_prefixes():
            cond = prefix.lower()
            estimated_date_from_ago(
                cleaned_data=self.cleaned_data, ago_field=f"{cond}_test_ago"
            )
            self.when_tested_required(cond=cond)
            self.applicable_if(YES, field=f"{cond}_test", field_applicable=f"{cond}_dx")

    def when_tested_required(self, cond=None):
        if self.cleaned_data.get(f"{cond}_test") == YES:
            if not self.cleaned_data.get(f"{cond}_test_ago") and not self.cleaned_data.get(
                f"{cond}_test_date"
            ):
                label = get_diagnosis_labels().get(cond)
                raise self.raise_validation_error(
                    (
                        f"When was the subject tested for {label}? Either provide an "
                        f"estimated time 'ago' or provide the exact date. See {label} "
                        "section below."
                    ),
                    MISSING_TEST_DATE,
                )
