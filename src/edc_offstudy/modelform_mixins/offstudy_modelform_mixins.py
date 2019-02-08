from django import forms

from ..utils import off_all_schedules_or_raise, OffstudyError


class OffstudyModelFormMixin(forms.ModelForm):

    """ModelForm mixin for the Offstudy Model.
    """

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data["subject_identifier"] = (
            cleaned_data.get("subject_identifier") or self.instance.subject_identifier
        )
        try:
            off_all_schedules_or_raise(
                subject_identifier=cleaned_data.get("subject_identifier"),
                offstudy_datetime=cleaned_data.get("offstudy_datetime"),
            )
        except OffstudyError as e:
            raise forms.ValidationError(e)
        return cleaned_data
