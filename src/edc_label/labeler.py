from django.apps import apps as django_apps

from .label import Label
from .print_server import PrintServer


app_config = django_apps.get_app_config('edc_label')


class Labeler:

    print_server_error = None
    print_server_cls = PrintServer
    label_cls = Label

    def __init__(self, *args, **kwargs):
        self.printers = {}
        self.label_templates = app_config.label_templates
        self.print_server = self.print_server_cls()
        for printer in self.print_server.printers.items():
            printer = str(printer[0])
            printer_properties = {
                k.replace('-', '_'):
                v for k, v in self.print_server.printers[printer].items()}
            self.printers.update({printer: printer_properties})

    def print_label(self, template_name, copies=None, context=None):
        copies = 3 if copies is None else copies
        label = self.label_cls(template_name=template_name)
        return label.print_label(copies, context=context)
