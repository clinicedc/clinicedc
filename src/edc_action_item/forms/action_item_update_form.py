from django import forms

from ..models import ActionItemUpdate


class ActionItemUpdateForm(forms.ModelForm):

    class Meta:
        model = ActionItemUpdate
        fields = '__all__'
