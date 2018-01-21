import os
import socket
import sys

from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings
from django.core.management.color import color_style

style = color_style()


class EdcLabelAppConfigError(Exception):
    pass


class AppConfig(DjangoAppConfig):
    name = 'edc_label'

    verbose_name = 'Edc Label'
    # full path to static templates folder
    template_folder = os.path.join(
        settings.STATIC_ROOT, 'edc_label', 'label_templates')
    # default extension
    template_ext = 'lbl'

    label_templates = {}

    def ready(self):
        sys.stdout.write(f'Loading {self.verbose_name} ...\n')
        if not os.path.exists(self.template_folder):
            os.makedirs(self.template_folder)
        for filename in os.listdir(self.template_folder):
            if filename.endswith(self.template_ext):
                label_name = filename.split('.')[0]
                self.label_templates.update({label_name: filename})
                sys.stdout.write(f' * {filename}\n')
        sys.stdout.write(f' Done loading {self.verbose_name}.\n')

    @property
    def default_cups_server(self):
        try:
            default_cups_server = socket.gethostbyname(
                self.default_cups_server_fqdn)
        except TypeError:
            try:
                default_cups_server = socket.gethostbyname(
                    self.default_cups_server_ip)
            except TypeError:
                default_cups_server = None
        return default_cups_server
