import json

from django.apps import apps as django_apps
from django.http.response import HttpResponse

from .labeler import Labeler

app_config = django_apps.get_app_config('edc_label')


class EdcLabelViewMixin:

    labeler_cls = Labeler

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.labeler = self.labeler_cls()

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.is_ajax():
            response_data = {}
            if self.kwargs.get('label_name'):
                label = self.labeler.print_label(self.kwargs.get('label_name'))
                response_data.update({
                    'label_message': label.message,
                    'label_error_message': label.error_message,
                    'print_server_error': label.print_server.error_message,
                })
            else:
                print('label_templates', {
                      label: (label_template.__dict__
                              for label, label_template in self.labeler.label_templates.items())})
                response_data.update({
                    'label_templates': json.dumps(
                        {label: (label_template.__dict__
                                 for label, label_template in self.labeler.label_templates.items())}),
                    'print_server': json.dumps(self.labeler.print_server.to_dict()),
                    'print_server_error': self.labeler.print_server.error_message,
                    'default_printer_name': self.labeler.default_printer_name,
                    'default_cups_server_ip': self.labeler.default_cups_server_ip,
                    'printers': json.dumps(self.labeler.printers),
                })
            return HttpResponse(json.dumps(response_data),
                                content_type='application/json')
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_name = context.get('project_name')
        context.update({
            'project_name': f'{project_name}: {self.verbose_name}',
            'default_cups_server_ip': self.labeler.default_cups_server_ip,
        })
        return context
