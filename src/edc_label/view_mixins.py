import json

from django.apps import apps as django_apps
from django.http.response import HttpResponse
from django.views.generic.base import ContextMixin
from django.contrib import messages

from .constants import CLINIC_LABEL_PRINTER, LAB_LABEL_PRINTER
from .labeler import Labeler
from .print_server import PrintServerSelectPrinterError, PrintServer
from edc_base.models import UserProfile

app_config = django_apps.get_app_config('edc_label')


class EdcLabelViewMixin(ContextMixin):

    labeler_cls = Labeler
    clinic_label_printer_attr = CLINIC_LABEL_PRINTER
    lab_label_printer_attr = LAB_LABEL_PRINTER

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.labeler = None
        self._user_profile = None

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
    def clinic_label_printer(self):
        return self.request.session.get(
            CLINIC_LABEL_PRINTER,
            getattr(self.user_profile, CLINIC_LABEL_PRINTER))

    @property
    def lab_label_printer(self):
        return self.request.session.get(
            LAB_LABEL_PRINTER,
            getattr(self.user_profile, LAB_LABEL_PRINTER))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            self.labeler = self.labeler_cls(request=self.request)
        except PrintServerSelectPrinterError as e:
            messages.error(self.request, str(e))
            default_cups_server_ip = None
            ps = PrintServer()
            printers = ps.printers
        else:
            default_cups_server_ip = self.labeler.print_server.ip_address
            printers = self.labeler.printers

        context.update({
            'default_cups_server_ip': default_cups_server_ip,
            CLINIC_LABEL_PRINTER: self.clinic_label_printer,
            LAB_LABEL_PRINTER: self.lab_label_printer,
            'printers': printers,
            f'{CLINIC_LABEL_PRINTER}_attr': CLINIC_LABEL_PRINTER,
            f'{LAB_LABEL_PRINTER}_attr': LAB_LABEL_PRINTER,
        })
        return context
