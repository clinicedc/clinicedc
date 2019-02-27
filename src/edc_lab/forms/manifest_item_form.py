from django import forms

from ..models import ManifestItem


class ManifestItemForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = ManifestItem
