from django import forms
from edc_constants.constants import CLOSED, OPEN, NEW

from ..constants import RESOLVED, REJECTED
from ..models import ActionItem


class ActionItemForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        self.raise_on_items_require_followup()
        self.force_open_status()
        return cleaned_data

    def force_open_status(self):
        """Sets status to open for edited NEW action items.
        """
        if self.instance.id and self.cleaned_data.get('status') == NEW:
            self.cleaned_data['status'] = OPEN

    def raise_on_items_require_followup(self):
        """Raises an exception if "not closed" inline
        records exist for this action item.
        """
        closed = [CLOSED, RESOLVED, REJECTED]
        inline = 'actionitemupdate_set'
        if f'{inline}-TOTAL_FORMS' in self.data:
            total_forms = int(self.data.get(f'{inline}-TOTAL_FORMS', 0))
            if (self.cleaned_data.get('status') in closed
                    and total_forms > 0):
                keys = [k for k in self.data.keys() if k.startswith(inline)
                        and k.endswith('closed')]
                if len(keys) < total_forms:
                    raise forms.ValidationError({
                        'status':
                        f'Invalid status. Cannot be set to {self.cleaned_data.get("status")}. '
                        f'Updates exist for this action item that have not been closed. '
                        f'See updates below.'})
        else:
            if (self.cleaned_data.get('status') in closed
                    and self.instance.actionitemupdate_set.exclude(closed=True).count() > 0):
                raise forms.ValidationError({
                    'status':
                    f'Invalid status. Cannot be set to {self.cleaned_data.get("status")}. '
                    f'Updates exist for this action item that have not been closed.'})

    class Meta:
        model = ActionItem
        fields = '__all__'
