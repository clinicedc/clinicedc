import json

from django.apps import apps as django_apps
from django.http.response import HttpResponse
from django.views.generic.base import ContextMixin
from django.contrib import messages

from .labeler import Labeler
from edc_label.print_server import PrintServerSelectPrinterError

app_config = django_apps.get_app_config('edc_label')


class EdcLabelViewMixin(ContextMixin):

    labeler_cls = Labeler

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.labeler = None

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.is_ajax():
            self.labeler = self.labeler_cls()
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
        try:
            self.labeler = self.labeler_cls()
        except PrintServerSelectPrinterError as e:
            messages.error(self.request, str(e))
            default_cups_server_ip = None
        else:
            default_cups_server_ip = self.labeler.default_cups_server_ip
        context.update({
            'default_cups_server_ip': default_cups_server_ip,
        })
        return context
