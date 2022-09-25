from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms

if TYPE_CHECKING:
    from edc_crf.crf_form_validator import CrfFormValidator
    from edc_crf.form_validator_mixins import CrfFormValidatorMixin
    from edc_crf.modelform_mixins import InlineCrfModelFormMixin

    from ..model_mixins import VisitModelMixin
    from ..modelform_mixins import VisitTrackingCrfModelFormMixin


def get_related_visit(
    modelform: (
        VisitTrackingCrfModelFormMixin
        | InlineCrfModelFormMixin
        | CrfFormValidator
        | CrfFormValidatorMixin
    ),
    related_visit_model_attr: str = None,
) -> VisitModelMixin | None:
    """Returns the related visit mode instance or None.

    Tries instance and cleaned data.
    """
    if related_visit_model_attr not in modelform.cleaned_data:
        related_visit = modelform.instance.related_visit
        if not related_visit:
            raise forms.ValidationError(f"Field `{related_visit_model_attr}` is required (2).")
    else:
        related_visit = modelform.cleaned_data.get(related_visit_model_attr)
    return related_visit
