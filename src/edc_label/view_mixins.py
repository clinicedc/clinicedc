import json

from django.apps import apps as django_apps
from django.http.response import HttpResponse

from .mixins import EdcLabelMixin


class EdcLabelViewMixin(EdcLabelMixin):

    def __init__(self, **kwargs):
        app_config = django_apps.get_app_config('edc_label')
        self._print_server = None
        self._printers = {}
        self.cups_server_ip = app_config.default_cups_server_ip
        self.default_printer_label = app_config.default_printer_label
        self.default_cups_server_ip = app_config.default_cups_server_ip or 'localhost'
        self.verbose_name = app_config.verbose_name
        self.label_templates = app_config.label_templates
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
                        {label: label_template.__dict__ for label, label_template in self.label_templates.items()}),
                    'print_server': json.dumps(self.print_server.to_dict()),
                    'print_server_error': self.print_server.error_message,
                    'default_printer_label': self.default_printer_label,
                    'default_cups_server_ip': self.default_cups_server_ip,
                    'printers': json.dumps(self.printers),
                })
            return HttpResponse(json.dumps(response_data), content_type='application/json')
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(EdcLabelViewMixin, self).get_context_data(**kwargs)
        context.update({
            'project_name': '{}: {}'.format(context.get('project_name'), self.verbose_name),
            'default_cups_server_ip': self.default_cups_server_ip,
        })
        return context
