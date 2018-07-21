from django.apps import apps as django_apps
from edc_label.label import Label
from edc_label.print_server import PrintServer


class PrintButtonAdminMixin:
    print_server_error = None

    def __init__(self, args, *kwargs):
        super(PrintButtonAdminMixin, self).__init__(*args, **kwargs)
        app_config = django_apps.get_app_config('edc_label')
        self._print_server = None
        self._printers = {}
        self.cups_server_ip = app_config.default_cups_server_ip
        self.label_templates = app_config.label_templates
        self.printer_label = app_config.default_printer_label

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
                    printer_properties = {
                        k.replace('-', '_'): v
                        for k, v in self.print_server.printers[printer].items()}
                    self._printers.update({printer: printer_properties})
        return self._printers

    def print_label(self, label_name, copies=None, context=None):
        copies = 1 if copies is None else copies
        label_template = self.label_templates.get(label_name)
        context = label_template.test_context if context is None else context
        label = Label(label_name, print_server=self.print_server,
                      context=context)
        label.print_label(copies)
        return label
