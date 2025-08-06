from django import forms

from edc_pylabels.models import LabelConfiguration
from edc_pylabels.site_label_configs import site_label_configs


class LabelConfigurationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].choices = [(k, k) for k in site_label_configs.all()]

    name = forms.ChoiceField(choices=[])

    def clean(self):
        cleaned_data = super().clean()
        if (
            "name" in cleaned_data
            and cleaned_data.get("name")
            and cleaned_data.get("name") not in site_label_configs.all()
        ):
            raise forms.ValidationError(
                "Invalid name. Name not registered with site_label_configs. "
                f"Expected one of {list(site_label_configs.all().keys())}"
            )
        return cleaned_data

    class Meta:
        model = LabelConfiguration
        fields = "__all__"
