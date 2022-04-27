from django import forms

from .models import SubjectScheduleHistory


class SubjectScheduleHistoryForm(forms.ModelForm):
    def clean(self):
        raise forms.ValidationError(
            "This is not a user form. This form may only be edited by the system."
        )

    class Meta:
        model = SubjectScheduleHistory
        fields = "__all__"
