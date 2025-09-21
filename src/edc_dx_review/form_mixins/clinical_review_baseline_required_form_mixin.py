from django import forms
from django.core.exceptions import ObjectDoesNotExist
from edc_model.utils import model_exists_or_raise

from ..utils import get_clinical_review_baseline_model_cls


class ClinicalReviewBaselineRequiredModelFormMixin:
    """Asserts Baseline Clinical Review exists or raise"""

    def clean(self) -> dict:
        cleaned_data = super().clean()
        model_cls = get_clinical_review_baseline_model_cls()
        if self._meta.model != model_cls and cleaned_data.get("subject_visit"):
            try:
                model_exists_or_raise(
                    subject_visit=cleaned_data.get("subject_visit"),
                    model_cls=model_cls,
                    singleton=True,
                )
            except ObjectDoesNotExist:
                raise forms.ValidationError(
                    f"Complete the `{model_cls._meta.verbose_name}` CRF first."
                )
        return cleaned_data
