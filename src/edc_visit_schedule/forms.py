from django import forms

from .models import MembershipForm


class MembershipFormForm(forms.ModelForm):

    class Meta:
        model = MembershipForm
        fields = '__all__'

    def clean(self):
        cleaned_data = self.cleaned_data
        try:
            cleaned_data.get('content_type_map').model_class().prepare_appointments
        except AttributeError:
            raise forms.ValidationError(
                'Membership forms must be a subclass of AppointmentMixin. See module appointment_helper.')
        return cleaned_data
