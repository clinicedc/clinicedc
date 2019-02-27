from django import forms

from ..models import BoxItem


class BoxItemForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = BoxItem
