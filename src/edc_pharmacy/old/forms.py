from django import forms

from .models import Prescription, Appointment, WorkList


class AppointmentForm(forms.ModelForm):

    class Meta:
        model = Appointment
        fields = '__all__'


class PrescriptionForm(forms.ModelForm):

    subject_identifier = forms.CharField(
        label='Subject identifier',
        help_text='(Read only)',
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    sid = forms.CharField(
        label='Randomization ID',
        help_text='(Read only)',
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    arm = forms.CharField(
        label='Randomization Arm',
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    result = forms.CharField(
        label='Auto calculated required quantity',
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = Prescription
        fields = '__all__'


class WorklistForm(forms.ModelForm):

    class Meta:
        model = WorkList
        fields = '__all__'
