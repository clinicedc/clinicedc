from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms

from ..exceptions import RelatedVisitFieldError

if TYPE_CHECKING:
    from edc_crf.crf_form_validator import CrfFormValidator
    from edc_crf.crf_form_validator_mixins import CrfFormValidatorMixin
    from edc_crf.modelform_mixins import InlineCrfModelFormMixin
    from edc_metadata.model_mixins.creates import CreatesMetadataModelMixin
    from edc_model.models import BaseUuidModel
    from edc_sites.model_mixins import SiteModelMixin
    from edc_visit_tracking.model_mixins import VisitModelMixin as Base

    from ..modelform_mixins import VisitTrackingCrfModelFormMixin

    class RelatedVisitModel(SiteModelMixin, CreatesMetadataModelMixin, Base, BaseUuidModel):
        pass


__all__ = ["get_related_visit"]


def get_related_visit(
    modelform: (
        VisitTrackingCrfModelFormMixin
        | InlineCrfModelFormMixin
        | CrfFormValidator
        | CrfFormValidatorMixin
    ),
    related_visit_model_attr: str | None = None,
) -> RelatedVisitModel | None:
    """Returns the related visit model instance or None.

    Tries instance and cleaned data.
    """
    if related_visit_model_attr not in modelform.cleaned_data:
        try:
            related_visit = modelform.instance.related_visit
        except RelatedVisitFieldError:
            related_visit = None
        if not related_visit:
            raise forms.ValidationError(
                f"This field is required. Got `{related_visit_model_attr}.` (2)."
            )
    else:
        related_visit = modelform.cleaned_data.get(related_visit_model_attr)
    return related_visit
