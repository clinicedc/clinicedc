from django import forms

from ..offstudy_crf import OffstudyCrf, SubjectOffstudyError


class OffstudyCrfModelFormMixin(forms.ModelForm):

    """ModelForm mixin for CRF Models.
    """

    offstudy_cls = OffstudyCrf

    def clean(self):
        cleaned_data = super().clean()
        subject_visit = cleaned_data.get('subject_visit')
        offstudy_model = subject_visit.visit_schedule.offstudy_model
        try:
            self.offstudy_cls(
                subject_identifier=subject_visit.subject_identifier,
                offstudy_model=offstudy_model,
                **cleaned_data)
        except SubjectOffstudyError as e:
            raise forms.ValidationError({'report_datetime': e})
        return cleaned_data
