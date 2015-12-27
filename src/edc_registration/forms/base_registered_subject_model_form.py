from django import forms
from django.core.exceptions import ImproperlyConfigured


class BaseRegisteredSubjectModelForm(forms.ModelForm):

    """ Base model for model.form that need a key to RegisteredSubject."""

    def clean(self):
        cleaned_data = super(BaseRegisteredSubjectModelForm, self).clean()
        if 'registered_subject' not in dir(self._meta.model):
            raise ImproperlyConfigured(
                'Expected form Model class {0} to have field attr \'registered_subject\'.'.format(self._meta.model))
        return cleaned_data
