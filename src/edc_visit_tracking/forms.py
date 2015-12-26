from django import forms

from edc_constants.constants import (
    YES, DEAD, DEATH_VISIT, OFF_STUDY, LOST_VISIT, COMPLETED_PROTOCOL_VISIT, MISSED_VISIT, UNKNOWN, ALIVE)


class VisitTrackingFormMixin(object):

    participant_label = 'participant'

    def clean(self):
        cleaned_data = super(VisitTrackingFormMixin, self).clean()
        self.validate_presence()
        self.validate_reason_and_info_source()
        self.validate_survival_status_if_alive()
        self.validate_visit_reason_and_study_status()
        self._meta.model(**cleaned_data).has_previous_visit_or_raise(forms.ValidationError)
        return cleaned_data

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
        cleaned_data = self.cleaned_data
        if cleaned_data.get('is_present') == YES:
            if cleaned_data.get('survival_status') == UNKNOWN:
                raise forms.ValidationError(
                    'Survival status cannot be unknown if {participant} is present.'.format(
                        participant=self.participant_label))
            if cleaned_data.get('reason') in [MISSED_VISIT, LOST_VISIT, DEATH_VISIT]:
                raise forms.ValidationError(
                    'You indicated that the reason for the visit report is {reason} '
                    'but also that the {participant} is present. Please correct.'.format(
                        participant=self.participant_label,
                        reason=cleaned_data.get('reason')))

    def validate_visit_reason_and_study_status(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('reason') == DEATH_VISIT:
            if cleaned_data.get('survival_status') != DEAD:
                raise forms.ValidationError(
                    'A death is being reported. Select \'Deceased\' for survival status.')
            if cleaned_data.get('study_status') != OFF_STUDY:
                raise forms.ValidationError(
                    'This is a death report visit. Select \'off study\' '
                    'for the {participant}\'s current study status.'.format(
                        participant=self.participant_label))
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
                raise forms.ValidationError('Provide reason scheduled visit was missed.')
