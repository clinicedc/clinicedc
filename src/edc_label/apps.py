import os
import sys

from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings
from django.core.management.color import color_style

style = color_style()


class AppConfig(DjangoAppConfig):
    name = 'edc_label'

    verbose_name = 'Edc Label'
    # IP address of the CUPS server, if localhost leave as None
    default_cups_server_ip = None
    # CUPS name of the default printer
    default_printer_name = None
    # full path to static templates folder
    template_folder = os.path.join(
        settings.STATIC_ROOT, 'edc_label', 'label_templates')
    # default extension
    template_ext = 'lbl'

    def ready(self):
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))
