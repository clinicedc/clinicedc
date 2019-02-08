from django import forms

from ..utils import OffstudyError, raise_if_offstudy


class OffstudyCrfModelFormMixin(forms.ModelForm):

    """ModelForm mixin for CRF Models.
    """

    def clean(self):
        cleaned_data = super().clean()
        visit = cleaned_data.get(self._meta.model.visit_model_attr())
        try:
            raise_if_offstudy(
                subject_identifier=visit.subject_identifier,
                report_datetime=cleaned_data.get("report_datetime"),
                offstudy_model_cls=visit.visit_schedule.offstudy_model_cls,
            )
        except OffstudyError as e:
            raise forms.ValidationError(f"{e}")
        return cleaned_data
