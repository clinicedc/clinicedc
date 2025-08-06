from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms

from edc_screening.utils import (
    get_subject_screening_model_cls,
    get_subject_screening_or_raise,
)

from .review_fields_modelform_mixin import ReviewFieldsModelFormMixin

if TYPE_CHECKING:
    from edc_screening.model_mixins import ScreeningModelMixin

___all__ = ["CleanFieldsModelFormValidationMixin"]


class CleanFieldsModelFormValidationMixin(ReviewFieldsModelFormMixin):
    """A model form mixin calling the default `clean_xxxxx` django
    methods.

    Used by ConsentModelFormMixin.

    See also: ConsentModelFormValidationMixin
    """

    @property
    def subject_screening_model_cls(self) -> ScreeningModelMixin:
        return get_subject_screening_model_cls()

    @property
    def subject_screening(self):
        screening_identifier = self.cleaned_data.get(
            "screening_identifier"
        ) or self.initial.get("screening_identifier")
        if not screening_identifier:
            raise forms.ValidationError(
                "Unable to determine the screening identifier. "
                f"This should be part of the initial form data. Got {self.cleaned_data}"
            )
        return get_subject_screening_or_raise(screening_identifier, is_modelform=True)

    def clean_initials(self) -> str:
        initials = self.cleaned_data.get("initials")
        if initials and initials != self.subject_screening.initials:
            raise forms.ValidationError(
                "Initials do not match those submitted at screening. "
                f"Expected {self.subject_screening.initials}."
            )
        return initials
