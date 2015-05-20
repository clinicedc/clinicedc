from django import forms
from django.contrib.admin.widgets import AdminRadioSelect, AdminRadioFieldRenderer
from edc.base.form.forms import BaseModelForm
from edc.subject.contact.forms import BaseContactLogItemFormCleaner
from ..models import PreAppointmentContact
from ..choices import INFO_PROVIDER


class PreAppointmentContactForm (BaseModelForm):

    information_provider = forms.ChoiceField(
        label='Who answered?',
        choices=[('', 'None')] + list(INFO_PROVIDER),
        required=False,
        widget=AdminRadioSelect(renderer=AdminRadioFieldRenderer),
        )

    def clean(self):
        cleaned_data = self.cleaned_data
        BaseContactLogItemFormCleaner().clean(cleaned_data)
        return super(PreAppointmentContactForm, self).clean()

    class Meta:
        model = PreAppointmentContact
