import cups
import json
import socket

from django.apps import apps as django_apps
from django.conf import settings
from django.contrib import messages
from django.http.response import HttpResponse
from django.views.generic.base import ContextMixin
from edc_base.models import UserProfile

from .constants import CLINIC_LABEL_PRINTER, LAB_LABEL_PRINTER, PRINT_SERVER
from .labeler import Labeler


class PrinterProperties:
    def __init__(self, name=None, cups_properties=None):
        for k, v in cups_properties.items():
            k = k.replace('-', '_')
            setattr(self, k, v)
        self.name = name

    def __str__(self):
        return f'{self.printer_info or self.printer.name} ({self.printer_make_and_model})'

    def __repr__(self):
        return f'{self.__class__}(name={self.name})'


app_config = django_apps.get_app_config('edc_label')


class EdcLabelViewMixin(ContextMixin):

    labeler_cls = Labeler
    print_server_attr = PRINT_SERVER
    clinic_label_printer_attr = CLINIC_LABEL_PRINTER
    lab_label_printer_attr = LAB_LABEL_PRINTER

    def __init__(self, *args, **kwargs):
        self.labeler = None
        self._user_profile = None
        self._printers = {}
        super().__init__(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.is_ajax():
            self.labeler = self.labeler_cls(request=request)
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
                    'default_printer_name': self.lab_label_printer or self.labeler.default_printer_name,
                    'default_cups_server_ip': self.labeler.default_cups_server_ip,
                    'printers': json.dumps(self.labeler.printers),
                })
            return HttpResponse(json.dumps(response_data),
                                content_type='application/json')
        return self.render_to_response(context)

    @property
    def user_profile(self):
        if not self._user_profile:
            self._user_profile = UserProfile.objects.get(
                user=self.request.user)
        return self._user_profile

    @property
    def print_server(self):
        return self.request.session.get(
            PRINT_SERVER,
            getattr(self.user_profile, PRINT_SERVER))

    @property
    def clinic_label_printer_name(self):
        return self.request.session.get(
            CLINIC_LABEL_PRINTER,
            getattr(self.user_profile, CLINIC_LABEL_PRINTER))

    @property
    def lab_label_printer_name(self):
        return self.request.session.get(
            LAB_LABEL_PRINTER,
            getattr(self.user_profile, LAB_LABEL_PRINTER))

    @property
    def printers(self):
        if not self._printers:
            cups_printers = {}
            if self.print_server:
                if self.print_server == 'localhost':
                    ip_address = None
                else:
                    try:
                        ip_address = socket.gethostbyname(self.print_server)
                    except TypeError:
                        ip_address = self.print_server
                if ip_address:
                    conn = cups.Connection(ip_address)
                else:
                    conn = cups.Connection()
                try:
                    cups_printers = conn.getPrinters()
                except RuntimeError:
                    messages.error(
                        self.request, 'Unable to contact print server')
            for name, cups_properties in cups_printers.items():
                printer_properties = PrinterProperties(
                    name=name,
                    cups_properties=cups_properties)
                self._printers.update({name: printer_properties})
        return self._printers

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'print_servers': settings.CUPS_SERVERS,
            'selected_print_server': self.print_server,
            'selected_clinic_label_printer': self.printers.get(self.clinic_label_printer_name),
            'selected_lab_label_printer': self.printers.get(self.lab_label_printer_name),
            'printers': self.printers,
        })
        return context
