from django import forms

from edc_action_item.forms.action_item_form_mixin import ActionItemFormMixin

from ..models import DataDictionary


class DataDictionaryForm(ActionItemFormMixin, forms.ModelForm):

    class Meta:
        model = DataDictionary
        fields = "__all__"
