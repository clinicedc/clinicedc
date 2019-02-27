from django import forms
from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured

from ..utils import OffstudyError, raise_if_offstudy


class OffstudyNonCrfModelFormMixin(forms.ModelForm):

    """ModelForm mixin for non-CRF modelforms.
    """

    def clean(self):
        cleaned_data = super().clean()
        if (
            not self._meta.model._meta.offstudy_model_cls
            and not self._meta.model._meta.offstudy_model
        ):
            raise ImproperlyConfigured(
                f"Attribute offstudy_model not defined. See {repr(self)}."
            )
        try:
            raise_if_offstudy(
                subject_identifier=cleaned_data.get("subject_identifier"),
                report_datetime=cleaned_data.get("report_datetime"),
                offstudy_model_cls=(
                    self._meta.model._meta.offstudy_model_cls
                    or django_apps.get_model(self._meta.model._meta.offstudy_model)
                ),
            )
        except OffstudyError as e:
            raise forms.ValidationError(f"{e}")
        return cleaned_data
