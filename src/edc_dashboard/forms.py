from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_forms.bootstrap import FieldWithButtons, StrictButton


class SubjectSearchForm(forms.Form):

    search_term = forms.CharField(label='Subject', max_length=36)

    def __init__(self, *args, **kwargs):
        super(SubjectSearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = ''
        self.helper.form_id = 'form-subject-search'
        self.helper.form_method = 'post'
        self.helper.form_show_labels = False,
        self.helper.html5_required = True
        self.helper.layout = Layout(
            FieldWithButtons('search_term', StrictButton("Search", type='submit')),
        )
