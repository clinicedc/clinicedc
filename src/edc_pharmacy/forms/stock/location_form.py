from django import forms

from ...models import Location


class LocationForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        if (
            cleaned_data.get("name")
            and cleaned_data.get("site")
            and cleaned_data.get("name") != cleaned_data.get("site").name
        ):
            raise forms.ValidationError({"site": "Site does not match this location"})

        return cleaned_data

    class Meta:
        model = Location
        fields = "__all__"
