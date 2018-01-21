import cups
import urllib

from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse
from django.utils.text import slugify
from edc_label.label import PrintLabelError

from ...dashboard_templates import dashboard_templates


class InvalidPostError(Exception):
    pass


class ActionViewError(Exception):
    pass


app_name = 'edc_lab_dashboard'


class ActionView:

    form_action_selected_items_name = 'selected_items'
    label_cls = None
    post_action_url = None  # key exists in request.url_name_data
    redirect_querystring = {}
    template_name = dashboard_templates.get('home_template')
    valid_form_actions = []

    navbar_name = 'specimens'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._selected_items = []
        self.action = None

    @property
    def selected_items(self):
        """Returns a list of selected listboard items.
        """
        if not self._selected_items:
            self._selected_items = self.request.POST.getlist(
                self.form_action_selected_items_name) or []
        return self._selected_items

    @property
    def url_kwargs(self):
        """Returns the default dictionary to reverse the post url.
        """
        return {}

    def post(self, request, *args, **kwargs):
        action = slugify(self.request.POST.get('action', '').lower())
        if action not in self.valid_form_actions:
            raise InvalidPostError(
                f'Invalid form action in POST. Got {action}')
        else:
            self.action = action
        self.process_form_action(request=request)
        try:
            url_name = request.url_name_data[self.post_action_url]
        except KeyError as e:
            raise ActionViewError(
                f'Invalid action \'post_action_url\'. Got {e}. See {repr(self)}.')
        url = reverse(url_name, kwargs=self.url_kwargs)
        if self.redirect_querystring:
            url = f'{url}?{urllib.parse.urlencode(self.redirect_querystring)}'
        return HttpResponseRedirect(url)

    def process_form_action(self, request=None):
        """Override to conditionally handle the action POST attr.
        """
        pass

    def print_labels(self, pks=None, request=None):
        """Print labels for each selected item.

        See also: edc_lab AppConfig
        """
        job_results = []
        for pk in pks:
            label = self.label_cls(
                pk=pk, children_count=len(pks), request=request)
            try:
                job_result = label.print_label()
            except (PrintLabelError, cups.IPPError) as e:
                messages.error(self.request, str(e))
            else:
                job_results.append(job_result)
        return job_results
