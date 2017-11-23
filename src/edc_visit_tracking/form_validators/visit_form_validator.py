from django import forms
from edc_form_validators import FormValidator
from edc_constants.constants import YES, NO, DEAD, OFF_STUDY, UNKNOWN, ALIVE, PARTICIPANT

from ..constants import LOST_VISIT, COMPLETED_PROTOCOL_VISIT, MISSED_VISIT
from ..visit_sequence import VisitSequence, VisitSequenceError


class VisitFormValidator(FormValidator):

    participant_label = 'participant'
    visit_sequence_cls = VisitSequence

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.appointment = self.cleaned_data.get('appointment')
        self.reason = self.cleaned_data.get('reason')
        self.is_present = self.cleaned_data.get('is_present')
        self.info_source = self.cleaned_data.get('info_source')
        self.survival_status = self.cleaned_data.get('survival_status')
        self.last_alive_date = self.cleaned_data.get('last_alive_date')
        self.study_status = self.cleaned_data.get('study_status')
        self.reason_missed = self.cleaned_data.get('reason_missed')

    def clean(self):
        if not self.appointment:
            raise forms.ValidationError({
                'appointment': 'Appointment cannot be blank.'})

        self.validate_presence()
        self.required_if(
            ALIVE, DEAD, field='survival_status', field_required='last_alive_date')
        self.validate_visit_reason_and_study_status()
        self.required_if(
            MISSED_VISIT, field='reason', field_required='reason_missed')

        visit_sequence = self.visit_sequence_cls(
            appointment=self.appointment)
        try:
            visit_sequence.enforce_sequence()
        except VisitSequenceError as e:
            raise forms.ValidationError(e)

    def validate_presence(self):
        """Raise an exception if 'is_present' does not make sense
        relative to 'survival status', 'reason' and 'info_source'.
        """
        if self.is_present == YES:
            if self.survival_status in [UNKNOWN, DEAD]:
                survival_status = self.survival_status
                raise forms.ValidationError({
                    'survival_status':
                    f'Survival status cannot be \'{survival_status.lower()}\' '
                    f'if {self.participant} is present.'})
            if self.reason in [MISSED_VISIT, LOST_VISIT]:
                raise forms.ValidationError({
                    'reason':
                    'You indicated that the reason for the visit report '
                    f'is {self.reason} but also that the {self.participant_label} '
                    'is present. Please correct.'})
        elif self.is_present == NO:
            if self.infor_source == PARTICIPANT:
                raise forms.ValidationError({
                    'info_source':
                    f'Source of information cannot be from {self.participant} '
                    f'if {self.participant} is not present.'})

    def validate_visit_reason_and_study_status(self):
        """Raise an exception if reason is lost or completed and
        study status is not off study.
        """
        if self.reason == LOST_VISIT:
            if self.study_status != OFF_STUDY:
                raise forms.ValidationError({
                    'study_status'
                    f'The {self.participant} is reported as lost to follow-up. '
                    f'Select \'off study\' for the {self.participant}\'s '
                    f'current study status.'})
        elif self.reason == COMPLETED_PROTOCOL_VISIT:
            if self.study_status != OFF_STUDY:
                raise forms.ValidationError({
                    'study_status':
                    f'The {self.participant} is reported as having completed the '
                    f'protocol. Select \'off study\' for the {self.participant}\'s '
                    f'current study status.'})
