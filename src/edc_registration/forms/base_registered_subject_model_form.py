from django.core.exceptions import ImproperlyConfigured
from edc.base.form.forms import BaseModelForm


class BaseRegisteredSubjectModelForm(BaseModelForm):

    """ Base model for model.form that need a key to RegisteredSubject."""

    def clean(self):
        cleaned_data = super(BaseRegisteredSubjectModelForm, self).clean()
        if not 'registered_subject' in dir(self._meta.model):
            raise ImproperlyConfigured('Expected form Model class {0} to have field attr \'registered_subject\'.'.format(self._meta.model))
        return cleaned_data
