from django import forms
from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured

from .constants import CLOSED_TIMEPOINT


class TimepointFormMixin:
    def clean(self):
        cleaned_data = super(TimepointFormMixin, self).clean()
        app_config = django_apps.get_app_config("edc_timepoint")
        try:
            app_config.timepoints[self._meta.model._meta.label_lower]
        except KeyError:
            raise ImproperlyConfigured(
                "ModelForm uses a model that is not a timepoint. "
                f"Got {self._meta.model._meta.label_lower}."
            )
        timepoint_status = cleaned_data.get("timepoint_status")
        if timepoint_status == CLOSED_TIMEPOINT:
            raise forms.ValidationError(
                f"This '{self._meta.verbose_name}' record is closed "
                "for data entry. See Timepoint."
            )
        return cleaned_data
