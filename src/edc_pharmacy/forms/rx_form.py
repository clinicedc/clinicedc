from django import forms
from edc_randomization.site_randomizers import site_randomizers

from ..models import Rx


def get_last_weight():
    return 100


class RxForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["randomizer_name"] = forms.ChoiceField(
            label="Randomizer name",
            choices=site_randomizers.get_as_choices(),
            required=False,
        )

    subject_identifier = forms.CharField(
        label="Subject Identifier",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    class Meta:
        model = Rx
        fields = "__all__"
