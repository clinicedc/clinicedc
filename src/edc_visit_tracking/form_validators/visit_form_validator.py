from django import forms
from edc_base.modelform_validators import FormValidator
from edc_constants.constants import YES, NO, DEAD, OFF_STUDY, UNKNOWN, ALIVE, PARTICIPANT

from ..constants import LOST_VISIT, COMPLETED_PROTOCOL_VISIT, MISSED_VISIT
from ..model_mixins import PreviousVisitError


class VisitFormValidator(FormValidator):

    participant_label = 'participant'
    requires_previous_visit = True

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
            MISSED_VISIT, field='reason', field_required='info_source')
        self.required_if(
            ALIVE, DEAD, field='survival_status', field_required='last_alive_date')

        self.validate_visit_reason_and_study_status()

        self.required_if(
            MISSED_VISIT, field='reason', field_required='reason_missed')

        self.validate_previous_visit()

    def validate_previous_visit(self):
        previous_visit_code = self.appointment.visits.previous(
            self.appointment.visit_code)
        if self.requires_previous_visit and previous_visit_code:
            if self.appointment.previous_visit:
                has_previous_visit = True
            elif (self.appointment.timepoint == 0
                  and self.appointment.rbase == 0):
                has_previous_visit = True
            else:
                has_previous_visit = False
            if not has_previous_visit:
                raise forms.ValidationError(
                    'Previous visit report required. Enter report for '
                    f'\'{previous_visit_code}\' before completing this report.')

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
