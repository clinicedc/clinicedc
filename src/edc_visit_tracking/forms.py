from django import forms

from edc_constants.constants import (
    YES, NO, DEAD, OFF_STUDY, LOST_VISIT, COMPLETED_PROTOCOL_VISIT, MISSED_VISIT, UNKNOWN, ALIVE, PARTICIPANT)
from django.core.exceptions import ObjectDoesNotExist


class VisitFormMixin(object):

    participant_label = 'participant'

    def clean(self):
        cleaned_data = super(VisitFormMixin, self).clean()
        self.validate_appointment_required()
        self.validate_against_consent()
        self.validate_time_point_status()
        self.validate_presence()
        self.validate_reason_and_info_source()
        self.validate_survival_status_if_alive()
        self.validate_visit_reason_and_study_status()
        self.validate_reason_visit_missed()
        self._meta.model(**cleaned_data).has_previous_visit_or_raise(forms.ValidationError)
        return cleaned_data

    def validate_appointment_required(self):
        cleaned_data = self.cleaned_data
        if not cleaned_data.get('appointment'):
            raise forms.ValidationError('Appointment cannot be blank.')

    def validate_against_consent(self):
        """Raises an exception if dates dont make sense with the consent.

        Note: subjects like infants don't have a consent model so attribute "consent_model"
        should be the birth model, just needs to have a dob."""
        cleaned_data = self.cleaned_data
        appointment = cleaned_data.get('appointment')
        try:
            consent = self._meta.model.consent_model.objects.get(
                registered_subject=appointment.registered_subject)
        except ObjectDoesNotExist:
            raise forms.ValidationError(
                '\'{}\' does not exist for subject.'.format(self._meta.model.consent_model._meta.verbose_name))
        try:
            if cleaned_data.get("report_datetime") < consent.consent_datetime:
                raise forms.ValidationError("Report datetime cannot be before consent datetime")
        except AttributeError:
            pass
        if cleaned_data.get("report_datetime").date() < consent.dob:
            raise forms.ValidationError("Report datetime cannot be before DOB")

    def validate_time_point_status(self):
        cleaned_data = self.cleaned_data
        appointment = cleaned_data.get('appointment')
        appointment.time_point_status_open_or_raise(exception_cls=forms.ValidationError)

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
#         if cleaned_data.get('survival_status') in [ALIVE, UNKNOWN]:
#             try:
#                 options = {
#                     '{}__appointment__registered_subject'.format(self._meta.model.visit_model_attr):
#                     cleaned_data.get(self._meta.model.visit_model_attr).appointment.registered_subject
#                 }
#                 death_report = self._meta.model.death_report_model.objects.get(**options)
#                 if death_report.death_date < cleaned_data.get():
#                     raise forms.ValidationError(
#                         'Participant was reported deceased on {}. '
#                         'Survival status cannot be {}'.format(
#                             death_report.death_date.strftime('%Y-%m-%d'),
#                             cleaned_data.get('survival_status')))
#             except self._meta.model.death_report_model.DoesNotExist:
#                 pass

    def validate_presence(self):
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
