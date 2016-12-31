from django import forms

from crispy_forms.bootstrap import FieldWithButtons, StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout


class SearchForm(forms.Form):

    search_term = forms.CharField(
        label='Search',
        max_length=36,
        required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = None  # set in child class
        self.helper.form_id = 'form-search'
        self.helper.form_method = 'post'
        self.helper.form_show_labels = False
        self.helper.html5_required = False
        self.helper.layout = Layout(
            FieldWithButtons('search_term', StrictButton('<i class="fa fa-search fa-sm"></i>', type='submit')))
