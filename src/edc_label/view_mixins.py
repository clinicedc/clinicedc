import json

from django.http.response import HttpResponse

from edc_label.label import app_config, Label
from edc_label.print_server import PrintServer


class EdcLabelViewMixin:

    print_server_error = None

    def __init__(self, **kwargs):
        self._print_server = None
        self._printers = {}
        self.cups_server_ip = app_config.default_cups_server_ip
        self.printer_label = app_config.default_printer_label
        super(EdcLabelViewMixin, self).__init__(**kwargs)

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
        context = super(EdcLabelViewMixin, self).get_context_data(**kwargs)
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

    def print_label(self, label_name, copies=None, context=None):
        copies = 3 if copies is None else copies
        label_template = app_config.label_templates.get(label_name)
        context = label_template.test_context if context is None else context
        label = Label(label_name, print_server=self.print_server, context=context)
        label.print_label(copies)
        return label
