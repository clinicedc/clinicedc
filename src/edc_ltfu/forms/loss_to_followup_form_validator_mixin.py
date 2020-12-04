from django import forms
from django.conf import settings
from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from edc_constants.constants import LOST_TO_FOLLOWUP

lftu_model_name = getattr(settings, "EDC_LFTU_MODEL_NAME", None)


class LossToFollowupFormValidatorMixin:

    loss_to_followup_model = lftu_model_name
    offschedule_reason_field = "offschedule_reason"

    @property
    def loss_to_followup_model_cls(self):
        return django_apps.get_model(self.loss_to_followup_model)

    def validate_ltfu(self):

        subject_identifier = (
            self.cleaned_data.get("subject_identifier")
            or self.instance.subject_identifier
        )

        try:
            self.loss_to_followup_model_cls.objects.get(
                subject_identifier=subject_identifier
            )
        except ObjectDoesNotExist:
            if self.offschedule_reason_field not in self.cleaned_data:
                raise ImproperlyConfigured(
                    "Unknown offschedule_reason_field. "
                    f"Got '{self.offschedule_reason_field}'. "
                    f"See form {self.__class__.__name__}"
                )
            if self.cleaned_data.get(self.offschedule_reason_field) == LOST_TO_FOLLOWUP:
                raise forms.ValidationError(
                    {
                        self.offschedule_reason_field: (
                            "Patient was lost to followup, please complete "
                            f"'{self.loss_to_followup_model_cls._meta.verbose_name}' "
                            "form first."
                        )
                    }
                )
