from django import forms
from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from edc_form_validators import FormValidator

from ..constants import LTFU
from ..utils import get_ltfu_model_name


class LtfuFormValidatorMixin(FormValidator):

    ltfu_model = get_ltfu_model_name()
    offschedule_reason_field = "offschedule_reason"

    @property
    def ltfu_model_cls(self):
        return django_apps.get_model(self.ltfu_model)

    def validate_ltfu(self):

        subject_identifier = (
            self.cleaned_data.get("subject_identifier") or self.instance.subject_identifier
        )

        try:
            self.ltfu_model_cls.objects.get(subject_identifier=subject_identifier)
        except ObjectDoesNotExist:
            if self.offschedule_reason_field not in self.cleaned_data:
                raise ImproperlyConfigured(
                    "Unknown offschedule_reason_field. "
                    f"Got '{self.offschedule_reason_field}'. "
                    f"See form {self.__class__.__name__}"
                )
            if self.cleaned_data.get(self.offschedule_reason_field) == LTFU:
                raise forms.ValidationError(
                    {
                        self.offschedule_reason_field: (
                            "Patient was lost to followup, please complete "
                            f"'{self.ltfu_model_cls._meta.verbose_name}' "
                            "form first."
                        )
                    }
                )
