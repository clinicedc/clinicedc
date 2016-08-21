import json

from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView

from edc_base.views.edc_base_view_mixin import EdcBaseViewMixin
from edc_label.label import app_config, Label
from edc_label.print_server import PrintServer


class HomeView(EdcBaseViewMixin, TemplateView):

    template_name = 'edc_label/home.html'
    print_server_error = None

    def __init__(self, **kwargs):
        self._print_server = None
        self._printers = {}
        self.cups_server_ip = app_config.default_cups_server_ip
        self.printer_label = app_config.default_printer_label
        super(HomeView, self).__init__(**kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.is_ajax():
            response_data = {}
            if self.kwargs.get('label_name'):
                label = self.print_label(self.kwargs.get('label_name'))
                response_data.update({
                    'label_message': label.message,
                    'label_error_message': label.error_message,
                    'print_server_error': label.print_server.error_message,
                })
            else:
                response_data.update({
                    'label_templates': json.dumps(
                        {label: label_template.__dict__ for label, label_template in app_config.label_templates.items()}),
                    'print_server': json.dumps(self.print_server.to_dict()),
                    'print_server_error': self.print_server.error_message,
                    'default_printer_label': app_config.default_printer_label,
                    'default_cups_server_ip': app_config.default_cups_server_ip or 'localhost',
                    'printers': json.dumps(self.printers),
                })
            return HttpResponse(json.dumps(response_data), content_type='application/json')
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context.update({
            'project_name': '{}: {}'.format(context.get('project_name'), app_config.verbose_name),
            'default_cups_server_ip': app_config.default_cups_server_ip or 'localhost',
        })
        return context

    @property
    def print_server(self):
        if not self._print_server:
            if self.cups_server_ip:
                self._print_server = PrintServer(self.cups_server_ip)
            else:
                self._print_server = PrintServer()
            self._print_server.select_printer(self.printer_label)
        return self._print_server

    @property
    def printers(self):
        if not self._printers:
            if self.print_server:
                for printer in self.print_server.printers.items():
                    printer = str(printer[0])
                    printer_properties = {k.replace('-', '_'): v for k, v in self.print_server.printers[printer].items()}
                    self._printers.update({printer: printer_properties})
        return self._printers

    def print_label(self, label_name):
        label_template = app_config.label_templates.get(label_name)
        label = Label(label_name, print_server=self.print_server, context=label_template.test_context)
        label.print_label(3)
        return label

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(HomeView, self).dispatch(*args, **kwargs)


class ModelPrint(HomeView):

    @property
    def model(self):
        return django_apps.get_model(self.kwargs.get('app_label'), self.kwargs.get('model_name'))

    def get_object(self):
        try:
            obj = self.model.get(pk=self.kwargs.get('pk'))
        except self.model.DoesNotExist:
            obj = None
        return obj

    @property
    def object(self):
        return self.get_object()

    def get_context_data(self, **kwargs):
        context = super(ModelPrint, self).get_context_data(**kwargs)
        try:
            label_context = self.object.to_label_context()
        except AttributeError:
            label_context = self.object.__dict__
        label = Label(label_context, self.kwargs.get('label_name'))
        label.print_label(self.kwargs.get('copies'), 1)
        context.update({
            'label_message': label.message,
            'label_error_message': label.error_message,
        })
        return context
