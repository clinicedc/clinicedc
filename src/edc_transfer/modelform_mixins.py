from django import forms
from django.core.exceptions import ObjectDoesNotExist
from edc_adverse_event.utils import get_ae_model


class SubjectTransferModelFormMixin:
    # verify transfer date is not on or after death
    def validate_death_date(self):
        if (
            self.cleaned_data.get("transfer_date")
            and getattr(self.death_report, "death_date", None)
            and self.cleaned_data.get("transfer_date") >= self.death_report.death_date
        ):
            raise forms.ValidationError("Invalid date. Cannot be on or after death_date")

    def death_report(self):
        try:
            return get_ae_model("death_report").objects.get(
                subject_identifier=self.cleaned_data.get("subject_identifier")
            )
        except ObjectDoesNotExist:
            return None
