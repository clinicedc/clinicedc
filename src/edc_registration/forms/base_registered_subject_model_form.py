from django.forms import ModelForm


class BaseRegisteredSubjectModelForm(ModelForm):

    """ Base model for model.form that need a key to RegisteredSubject.

    TODO: should confirm attr registered subject"""

    def clean(self):
        cleaned_data = super(BaseRegisteredSubjectModelForm, self).clean()
        return cleaned_data
