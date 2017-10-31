from django import forms

from ..models import Prescription


class PrescriptionForm(forms.ModelForm):

    #     subject_identifier = forms.CharField(
    #         label='Subject identifier',
    #         help_text='(Read only)',
    #         widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    #
    #     rando_sid = forms.CharField(
    #         label='Randomization ID',
    #         help_text='(Read only)',
    #         widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    #
    #     rando_arm = forms.CharField(
    #         label='Randomization Arm',
    #         help_text='(Read only)',
    #         widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    #     result = forms.CharField(
    #         label='Auto calculated required quantity',
    #         widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = Prescription
        fields = '__all__'
