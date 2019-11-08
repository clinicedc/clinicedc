from django import forms

from .utils import get_randomizationlist_model


class RandomizationListForm(forms.ModelForm):
    class Meta:
        model = get_randomizationlist_model()
        fields = "__all__"


class LimitedRandomizationListForm(forms.ModelForm):
    class Meta:
        model = get_randomizationlist_model()
        fields = [
            "subject_identifier",
            "sid",
            "site_name",
            "allocated",
            "allocated_datetime",
            "allocated_user",
        ]
