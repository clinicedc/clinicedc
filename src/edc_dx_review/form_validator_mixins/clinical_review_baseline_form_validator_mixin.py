from edc_visit_schedule.utils import raise_if_not_baseline


class ClinicalReviewBaselineFormValidatorMixin:
    def _clean(self):
        raise_if_not_baseline(self.cleaned_data.get("subject_visit"))
        super()._clean()
