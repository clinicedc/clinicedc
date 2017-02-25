from django import forms
from django.urls.base import reverse

from crispy_forms.bootstrap import FieldWithButtons, StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field


class SearchForm(forms.Form):

    action_url = None
    action_url_name = 'home_url'
    button_label = '<i class="fa fa-search fa-sm"></i>'

    q = forms.CharField(
        label='Search',
        max_length=150,
        required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        if self.action_url:
            self.helper.form_action = self.action_url
        else:
            self.helper.form_action = reverse(self.action_url_name)
        self.helper.form_id = 'form-search'
        self.helper.form_class = 'form-inline'
        self.helper.form_method = 'get'
        self.helper.form_show_labels = False
        self.helper.html5_required = False
        self.helper.layout = Layout(
            FieldWithButtons(
                Field(
                    'q', placeholder="search",
                    css_class="form-control input-sm"),
                StrictButton(
                    self.button_label, type='submit',
                    css_class="btn btn-default btn-sm")))
