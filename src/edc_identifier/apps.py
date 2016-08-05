import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style


class AppConfig(DjangoAppConfig):
    name = 'edc_identifier'
    verbose_name = 'Identifier'
    identifier_prefix = '999'  # e.g. 066 for BHP066
    identifier_modulus = 7

    def ready(self):
        style = color_style()
        if 'test' not in sys.argv:
            if self.identifier_prefix == '999':
                sys.stdout.write(style.NOTICE(
                    'Warning: \'identifier_prefix\' has not been explicitly set. '
                    'Using default \'999\'. See AppConfig.\n'))
