from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, ButtonHolder, Button
from django.urls.base import reverse


class SubjectForm(forms.Form):

    subject_identifier = forms.CharField(label='Subject', max_length=36)

    current_user = forms.BooleanField(label='limit search to current user', initial=False, required=False)

    def __init__(self, *args, **kwargs):
        super(SubjectForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper = FormHelper()
        self.helper.form_action = ''
        self.helper.form_style = 'inline'
        self.helper.form_id = 'form-subject-search'
        # self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.html5_required = True
        self.helper.layout = Layout(
            'subject_identifier', 'current_user',
            ButtonHolder(
                Button('show-most-recent-subjects', 'Show most recent'),
                Button('hide-most-recent-subjects', 'Hide most recent'),
                Submit('subject-search', 'Search', css_class="pull-right"),
            ))
