from django import forms
from edc_form_validators import FormValidator

from ..constants import MISSED_VISIT
from ..visit_sequence import VisitSequence, VisitSequenceError


class VisitFormValidator(FormValidator):

    visit_sequence_cls = VisitSequence

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def clean(self):
        appointment = self.cleaned_data.get('appointment')
        if not appointment:
            raise forms.ValidationError({
                'appointment': 'This field is required'})

        visit_sequence = self.visit_sequence_cls(appointment=appointment)
        try:
            visit_sequence.enforce_sequence()
        except VisitSequenceError as e:
            raise forms.ValidationError(e)

        self.required_if(
            MISSED_VISIT, field='reason', field_required='reason_missed')
