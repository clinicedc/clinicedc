import urllib

from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse
from django.utils.text import slugify
from django.views.generic.base import TemplateView
from edc_label import JobResult, PrintersMixin, PrinterError

from ...dashboard_templates import dashboard_templates


class InvalidPostError(Exception):
    pass


class ActionViewError(Exception):
    pass


app_name = 'edc_lab_dashboard'


class ActionView(PrintersMixin, TemplateView):

    form_action_selected_items_name = 'selected_items'
    label_cls = None
    job_result_cls = JobResult
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

    @property
    def printer(self):
        printer = self.lab_label_printer
        if not printer:
            messages.error(
                self.request,
                'Your "lab" label printer is not configured. '
                'See Edc Label in Administration.')
            raise PrinterError('lab_label_printer not set. Got None')
        return printer

    def print_labels(self, pks=None, request=None):
        """Returns a job_result object or None after printing.
        """
        zpl_data = b''
        try:
            printer = self.printer
        except PrinterError:
            printer = None
            job_id = None
            job_result = None
        else:
            for pk in pks:
                label = self.label_cls(
                    pk=pk, children_count=len(pks), request=request)
                zpl_data += label.render_as_zpl_data()
            job_id = printer.stream_print(zpl_data=zpl_data)
            job_result = self.job_result_cls(
                name=self.label_cls.label_template_name, copies=1, job_ids=[job_id],
                printer=printer)
        return job_result
