from django import forms
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from edc_adverse_event import get_ae_model
from edc_constants.constants import DWTA, OTHER
from edc_form_validators import FormValidator
from edc_utils import convert_php_dateformat

from .constants import TRANSFERRED


class SubjectTransferModelFormMixin:

    # verify transfer date is not on or after death
    def validate_death_date(self):
        if self.death_report.death_date <= self.cleaned_data.get("transfer_date"):
            raise forms.ValidationError()

    def death_report(self):
        try:
            return get_ae_model("death_report").objects.get(
                subject_identifier=self.cleaned_data.get("subject_identifier")
            )
        except ObjectDoesNotExist:
            return None


class SubjectTransferFormValidator(FormValidator):
    """For use with the SubjectTransferForm"""

    def clean(self):

        # verify on study

        self.validate_other_specify(
            "initiated_by", other_specify_field="initiated_by_other"
        )

        self.m2m_single_selection_if(DWTA, m2m_field="transfer_reason")

        self.m2m_other_specify(
            OTHER, m2m_field="transfer_reason", field_other="transfer_reason_other"
        )


class SubjectTransferFormValidatorMixin:
    """Used in off schedule form or any form that
    needs to confirm the Subject Transfer form was submitted
    first.

    Note: This mixin is NOT for use with the SubjectTransferForm.
    """

    subject_transfer_model = None  # "inte_prn.subjecttransfer"
    subject_transfer_date_field = "transfer_date"
    subject_transfer_reason = TRANSFERRED

    @property
    def subject_transfer_model_cls(self):
        return django_apps.get_model(self.subject_transfer_model)

    def validate_subject_transferred(self):
        if self.cleaned_data.get("subject_identifier") or self.instance:
            subject_identifier = (
                self.cleaned_data.get("subject_identifier")
                or self.instance.subject_identifier
            )
            try:
                subject_transfer_obj = django_apps.get_model(
                    self.subject_transfer_model
                ).objects.get(subject_identifier=subject_identifier)
            except ObjectDoesNotExist:
                if (
                    self.cleaned_data.get(self.offschedule_reason_field)
                    and self.cleaned_data.get(self.offschedule_reason_field).name
                    == self.subject_transfer_reason
                ):
                    msg = (
                        "Patient has been transferred, please complete "
                        f"`{self.subject_transfer_model_cls._meta.verbose_name}` "
                        "form first."
                    )
                    raise forms.ValidationError({self.offschedule_reason_field: msg})
            else:
                if self.cleaned_data.get(self.subject_transfer_date_field) and (
                    subject_transfer_obj.transfer_date
                    != self.cleaned_data.get(self.subject_transfer_date_field)
                ):
                    expected = subject_transfer_obj.transfer_date.strftime(
                        convert_php_dateformat(settings.SHORT_DATE_FORMAT)
                    )
                    got = self.cleaned_data.get(
                        self.subject_transfer_date_field
                    ).strftime(convert_php_dateformat(settings.SHORT_DATE_FORMAT))
                    raise forms.ValidationError(
                        {
                            self.subject_transfer_date_field: (
                                "Date does not match "
                                f"`{self.subject_transfer_model_cls._meta.verbose_name}` "
                                f"form. Expected {expected}. Got {got}."
                            )
                        }
                    )
