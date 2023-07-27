from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms
from django.core.exceptions import ObjectDoesNotExist

if TYPE_CHECKING:
    from .crf_model_form_mixin import CrfModelFormMixin

    class MyForm(CrfModelFormMixin, forms.ModelForm):
        pass


class CrfSingletonModelFormMixin:
    def raise_if_singleton_exists(self: MyForm) -> None:
        """Raise if singleton model instance exists at another
        timepoint.
        """
        if not self.instance.id:
            try:
                obj = self._meta.model.objects.get(
                    subject_visit__subject_identifier=self.subject_identifier
                )
            except ObjectDoesNotExist:
                pass
            else:
                raise forms.ValidationError(
                    f"Invalid.  This form has already been submittted. "
                    f"See '{obj.visit_code}.{obj.visit_code_sequence}'."
                )
