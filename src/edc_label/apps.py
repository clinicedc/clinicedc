import os

from django.conf import settings
from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = 'edc_label'
    default_cups_server_ip = None
    default_printer_name = None
    default_template_file = os.path.join(settings.STATIC_ROOT, 'edc_label', 'label_templates', 'default.txt')
    default_label_identifier_name = 'barcode_value'
