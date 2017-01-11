from django import forms
from django.urls.base import reverse

from crispy_forms.bootstrap import FieldWithButtons, StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout


class SearchForm(forms.Form):

    listboard_url_name = 'home_url'
    button_label = '<i class="fa fa-search fa-sm"></i>'

    search_term = forms.CharField(
        label='Search',
        max_length=36,
        required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = reverse(self.listboard_url_name)
        self.helper.form_id = 'form-search'
        self.helper.form_class = 'form-inline'
        self.helper.form_method = 'post'
        self.helper.form_show_labels = False
        self.helper.html5_required = False
        self.helper.layout = Layout(
            FieldWithButtons('search_term', StrictButton(self.button_label, type='submit')))
