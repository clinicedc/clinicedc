import urllib

from django.apps import apps as django_apps
from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse
from django.utils.text import slugify
from django.views.generic.base import TemplateView
from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import AppConfigViewMixin
from edc_label.label import PrintLabelError
from edc_label.print_server import PrintServerSelectPrinterError

from ..mixins.models_view_mixin import ModelsViewMixin


class InvalidPostError(Exception):
    pass


app_name = 'edc_lab_dashboard'
app_config = django_apps.get_app_config(app_name)


class BaseActionView(ModelsViewMixin, EdcBaseViewMixin,
                     AppConfigViewMixin, TemplateView):

    template_name = 'edc_lab_dashboard/home.html'
    post_url_name = None
    app_config_name = 'edc_lab_dashboard'

    valid_form_actions = []
    redirect_querystring = {}
    form_action_selected_items_name = 'selected_items'
    label_cls = None

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

    @property
    def post_url(self):
        """Returns a URL.
        """
        return reverse(self.post_url_name, kwargs=self.url_kwargs)

    def post(self, request, *args, **kwargs):
        action = slugify(self.request.POST.get('action', '').lower())
        if action not in self.valid_form_actions:
            raise InvalidPostError(
                'Invalid form action in POST. Got {}'.format(action))
        else:
            self.action = action
        self.process_form_action()
        if self.redirect_querystring:
            return HttpResponseRedirect(
                self.post_url + '?'
                + urllib.parse.urlencode(self.redirect_querystring))
        return HttpResponseRedirect(self.post_url)

    def process_form_action(self):
        """Override to conditionally handle the action POST attr.
        """
        pass

    def print_labels(self, pks=None):
        """Print labels for each selected item.

        See also: edc_lab AppConfig
        """
        for pk in pks:
            try:
                label = self.label_cls(pk=pk, children_count=len(pks))
            except PrintServerSelectPrinterError as e:
                messages.error(
                    self.request,
                    str(e), extra_tags='PrintServerSelectPrinterError')
                break
            else:
                try:
                    result = label.print_label()
                except PrintLabelError as e:
                    messages.error(self.request, str(e))
                else:
                    messages.success(
                        self.request,
                        f'Printed {result.print_count}/{result.copies} {result.name} to '
                        f'{result.printer}. JobID {result.jobid}')
