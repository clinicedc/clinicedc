from edc_model.utils import model_exists_or_raise

from ..utils import get_clinical_review_baseline_model_cls


class ClinicalReviewBaselineRequiredModelFormMixin:
    """Asserts Baseline Clinical Review exists or raise"""

    def clean(self):
        model_cls = get_clinical_review_baseline_model_cls()
        if self._meta.model != model_cls and self.cleaned_data.get("subject_visit"):
            model_exists_or_raise(
                subject_visit=self.cleaned_data.get("subject_visit"),
                model_cls=model_cls,
                singleton=True,
            )
        return super().clean()
