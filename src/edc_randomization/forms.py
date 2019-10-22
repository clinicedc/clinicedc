from django import forms

from .models import RandomizationList


class RandomizationListForm(forms.ModelForm):
    class Meta:
        model = RandomizationList
        fields = "__all__"


class LimitedRandomizationListForm(forms.ModelForm):
    class Meta:
        model = RandomizationList
        fields = [
            "subject_identifier",
            "sid",
            "site_name",
            "allocated",
            "allocated_datetime",
            "allocated_user",
        ]
