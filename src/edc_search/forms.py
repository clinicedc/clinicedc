from django import forms

from crispy_forms.bootstrap import FieldWithButtons, StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout


class SearchForm(forms.Form):

    search_term = forms.CharField(
        label='',
        max_length=36,
        required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper = FormHelper()
        self.helper.form_action = None
        self.helper.form_id = 'form-search'
        self.helper.form_method = 'post'
        # self.helper.html5_required = True
        self.helper.layout = Layout(
            FieldWithButtons('search_term', StrictButton('Search', type='submit')))
