from django.apps import apps as django_apps
from edc_label.label import Label


class PrintButtonAdminMixin:
    print_server_error = None

    def __init__(self, args, *kwargs):
        super(PrintButtonAdminMixin, self).__init__(*args, **kwargs)
        app_config = django_apps.get_app_config("edc_label")
        self._print_server = None
        self._printers = {}
        self.cups_server_ip = app_config.default_cups_server_ip
        self.label_templates = app_config.label_templates
        self.printer_label = app_config.default_printer_label

    def print_label(self, label_name, copies=None, context=None):
        copies = 1 if copies is None else copies
        label_template = self.label_templates.get(label_name)
        context = label_template.test_context if context is None else context
        label = Label(label_name)
        label.render_as_zpl_data(context=context, copies=copies)
        return label
