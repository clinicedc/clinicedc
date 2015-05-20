from django import forms
from django.db.models import get_model
from django.conf import settings

from edc.subject.consent.forms import BaseConsentedModelForm


class BaseVisitTrackingForm(BaseConsentedModelForm):

    def __init__(self, *args, **kwargs):
        super(BaseVisitTrackingForm, self).__init__(*args, **kwargs)
        self._validation_error = None

    def clean(self):
        cleaned_data = self.cleaned_data
        TimePointStatus = get_model('data_manager', 'TimePointStatus')
        TimePointStatus.check_time_point_status(cleaned_data.get('appointment'), exception_cls=forms.ValidationError)
        if 'edc.device.dispatch' in settings.INSTALLED_APPS:
            if cleaned_data.get('appointment', None):
                appointment = cleaned_data.get('appointment')
                dispatch_item = appointment.dispatched_item()
                if dispatch_item:
                    forms.ValidationError("Data for {0} is currently dispatched to netbook {1}. "
                                          "This form may not be modified.".format(appointment.registered_subject.subject_identifier,
                                                                                  dispatch_item.producer.name))
        self._validate_cleaned_data(cleaned_data)
        return super(BaseConsentedModelForm, self).clean()

    def set_validation_error(self, value=None):
        if value:
            if not isinstance(value, dict):
                raise TypeError('parameter value must be a dictionary.')
        self._validation_error = value

    def get_validation_error(self):
        if not self._validation_error:
            self.set_validation_error()
        return self._validation_error
