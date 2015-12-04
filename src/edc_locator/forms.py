import re

from django import forms
from django.conf import settings

from edc_constants.constants import YES


class LocatorFormMixin(forms.ModelForm):

    def clean(self):
        cleaned_data = super(LocatorFormMixin, self).clean()
        self.may_follow_up_requires_contacts()
        self.may_call_work_requires_contacts()
        self.home_visit_permission_requires_address()
        self.may_contact_someone_requires_contacts()
        return cleaned_data

    def clean_subject_work_phone(self):
        cleaned_data = self.cleaned_data
        subject_work_phone = cleaned_data['subject_work_phone']
        if subject_work_phone:
            cell_pattern = None
            tel_pattern = None
            try:
                cell_pattern = settings.CELLPHONE_REGEX
                cell = re.match(cell_pattern, subject_work_phone).group()
            except AttributeError:
                cell = None
            try:
                tel_pattern = settings.TELEPHONE_REGEX
                tel = re.match(tel_pattern, subject_work_phone).group()
            except AttributeError:
                tel = None
            if cell_pattern or tel_pattern:
                if not cell and not tel:
                    raise forms.ValidationError('Invalid phone number format. '
                                                'Expected either a valid cell number or a valid telephone number')
        return subject_work_phone

    def may_follow_up_requires_contacts(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('may_follow_up') == YES:
            if not cleaned_data.get('subject_cell') and not cleaned_data.get('subject_phone'):
                raise forms.ValidationError(
                    'Participant allows study staff to follow them up, provide a valid phone and/or cell number')
        else:
            for field in [('subject_cell', 'cell number'),
                          ('subject_cell_alt', 'alternative cell number'),
                          ('subject_phone', 'phone number'),
                          ('subject_phone_alt', 'alternative phone number')]:
                if cleaned_data.get(field[0]):
                    raise forms.ValidationError(
                        'Participant does not allow study staff to follow them up, '
                        'DO NOT provide the subject\'s {}'.format(field[1]))
        return cleaned_data

    def may_call_work_requires_contacts(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('may_call_work') == YES:
            if not cleaned_data.get('subject_work_place'):
                raise forms.ValidationError(
                    'Participant allows study staff to contact them at work, provide the work place location.')
            if not cleaned_data.get('subject_work_phone'):
                raise forms.ValidationError(
                    'Participant allows study staff to contact them at work, provide a valid work phone number.')
        else:
            if cleaned_data.get('subject_work_place'):
                raise forms.ValidationError(
                    'Participant does not allow study staff to contact them at work, '
                    'DO NOT provide the work place location')
            if cleaned_data.get('subject_work_phone'):
                raise forms.ValidationError(
                    'Participant does not allow study staff to contact them at work, '
                    ' DO NOT provide the work phone number.')
        return cleaned_data

    def home_visit_permission_requires_address(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('home_visit_permission') == YES:
            if not cleaned_data.get('physical_address'):
                raise forms.ValidationError(
                    'Participant allows study staff to visit them at home, '
                    'provide the participant\'s physical address.')
        else:
            if cleaned_data.get('physical_address'):
                raise forms.ValidationError(
                    'Participant does not allow study staff to visit them at home, '
                    'DO NOT provide the participant\'s physical address.')
        return cleaned_data

    def may_contact_someone_requires_contacts(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('may_contact_someone') == YES:
            if not cleaned_data.get('contact_name'):
                raise forms.ValidationError(
                    'Participant allows the study to contact someone else on their behalf, '
                    'provide the contact name.')
            if not cleaned_data.get('contact_rel'):
                raise forms.ValidationError(
                    'Participant allows the study to contact someone else on their behalf, '
                    'how are they related to this person?')
            if not cleaned_data.get('contact_physical_address'):
                raise forms.ValidationError(
                    'Participant allows the study to contact someone else on their behalf, '
                    'provide this person\'s physical address.')
        else:
            if cleaned_data.get('contact_name'):
                raise forms.ValidationError(
                    'Participant does not allow the study to contact someone else on their behalf, '
                    'DO NOT provide the contact name.')
            if cleaned_data.get('contact_rel'):
                raise forms.ValidationError(
                    'Participant does not allow the study to contact someone else on their behalf, '
                    'DO NOT indicate the relationship to this person.')
            if cleaned_data.get('contact_physical_address'):
                raise forms.ValidationError(
                    'Participant does not allow the study to contact someone else on their behalf, '
                    'DO NOT provide this person\'s physical address.')
        return cleaned_data
