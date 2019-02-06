from django import forms

from .models import SubjectScheduleHistory


class SubjectScheduleHistoryForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        raise forms.ValidationError(
            "This is not a user form. This form may only be edited by the system."
        )
        return cleaned_data

    class Meta:
        model = SubjectScheduleHistory
        fields = "__all__"
