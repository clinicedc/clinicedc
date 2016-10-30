from django import forms

from edc_constants.constants import YES, NO, DEAD, OFF_STUDY, UNKNOWN, ALIVE, PARTICIPANT

from .constants import LOST_VISIT, COMPLETED_PROTOCOL_VISIT, MISSED_VISIT


class VisitFormMixin:

    participant_label = 'participant'

    def clean(self):
        cleaned_data = super(VisitFormMixin, self).clean()
        self.validate_appointment_required()
        self.validate_presence()
        self.validate_reason_and_info_source()
        self.validate_survival_status_if_alive()
        self.validate_visit_reason_and_study_status()
        self.validate_reason_visit_missed()
        self._meta.model(
            visit_schedule_name=cleaned_data.get('appointment').visit_schedule_name,
            schedule_name=cleaned_data.get('appointment').schedule_name,
            visit_code=cleaned_data.get('appointment').visit_code,
            **cleaned_data).has_previous_visit_or_raise(forms.ValidationError)
        return cleaned_data

    def validate_appointment_required(self):
        cleaned_data = self.cleaned_data
        if not cleaned_data.get('appointment'):
            raise forms.ValidationError('Appointment cannot be blank.')

    def validate_reason_and_info_source(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('reason') != MISSED_VISIT:
            if not cleaned_data.get('info_source'):
                raise forms.ValidationError('Provide source of information.')

    def validate_survival_status_if_alive(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('survival_status') in [ALIVE, DEAD]:
            if not cleaned_data.get('last_alive_date'):
                raise forms.ValidationError(
                    'Provide date {participant} last known alive.'.format(participant=self.participant_label))

    def validate_presence(self):
        """Raise an exception if 'is_present' does not make sense relative to 'survival status',
        'reason' and 'info_source'."""
        cleaned_data = self.cleaned_data
        if cleaned_data.get('is_present') == YES:
            if cleaned_data.get('survival_status') in [UNKNOWN, DEAD]:
                raise forms.ValidationError(
                    'Survival status cannot be \'{survival_status}\' if {participant} is present.'.format(
                        survival_status=cleaned_data.get('survival_status').lower(),
                        participant=self.participant_label))
            if cleaned_data.get('reason') in [MISSED_VISIT, LOST_VISIT]:
                raise forms.ValidationError(
                    'You indicated that the reason for the visit report is {reason} '
                    'but also that the {participant} is present. Please correct.'.format(
                        participant=self.participant_label,
                        reason=cleaned_data.get('reason')))
        elif cleaned_data.get('is_present') == NO:
            if cleaned_data.get('info_source') == PARTICIPANT:
                raise forms.ValidationError(
                    'Source of information cannot be from {participant} if {participant} is not present.'.format(
                        participant=self.participant_label))

    def validate_visit_reason_and_study_status(self):
        """Raise an exception if reason is lost or completed and study status is not off study."""
        cleaned_data = self.cleaned_data
        if cleaned_data.get('reason') == LOST_VISIT:
            if cleaned_data.get('study_status') != OFF_STUDY:
                raise forms.ValidationError(
                    'The {participant} is reported as lost to follow-up. Select \'off study\' for '
                    'the {participant}\'s current study status.'.format(
                        participant=self.participant_label))
        if cleaned_data.get('reason') == COMPLETED_PROTOCOL_VISIT:
            if cleaned_data.get('study_status') != OFF_STUDY:
                raise forms.ValidationError(
                    'The {participant} is reported as having completed the protocol. '
                    'Select \'off study\' for the {participant}\'s current study status.'.format(
                        participant=self.participant_label))

    def validate_reason_visit_missed(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('reason') == MISSED_VISIT:
            if not cleaned_data.get('reason_missed'):
                raise forms.ValidationError('Provide reason visit was missed.')
        else:
            if cleaned_data.get('reason_missed'):
                raise forms.ValidationError(
                    'Visit was not missed, do not provide reason visit was missed.')
