from django import forms
from edc_constants.constants import CLOSED, OPEN, NEW

from ..constants import RESOLVED, REJECTED
from ..models import ActionItem


class ActionItemForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        self.raise_on_items_require_followup()
        if self.instance.id and cleaned_data.get('status') == NEW:
            cleaned_data['status'] = OPEN
        return cleaned_data

    def raise_on_items_require_followup(self):

        inline = 'actionitemupdate_set'
        total_forms = int(self.data.get(f'{inline}-TOTAL_FORMS', 0))
        if self.cleaned_data.get('status') in [CLOSED, RESOLVED, REJECTED] and total_forms > 0:
            keys = [k for k in self.data.keys() if k.startswith(inline)
                    and k.endswith('closed')]
            if len(keys) < total_forms:
                raise forms.ValidationError(
                    f'Invalid status. Cannot be set to {self.cleaned_data.get("status")}. '
                    f'Updates exist for this action item that have not been closed. '
                    f'See updates below.')

    class Meta:
        model = ActionItem
        fields = '__all__'
