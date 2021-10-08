from django import forms
from edc_randomization.site_randomizers import site_randomizers

from ..models import Prescription


def get_last_weight():
    return 100


class PrescriptionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["randomizer_name"] = forms.ChoiceField(
            label="Randomizer name",
            choices=site_randomizers.get_as_choices(),
            required=False,
        )

    class Meta:
        model = Prescription
        fields = "__all__"
