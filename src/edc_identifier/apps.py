import sys

from edc_device.apps import AppConfig as EdcDeviceAppConfigParent

from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style


class AppConfig(DjangoAppConfig):
    name = 'edc_identifier'
    verbose_name = 'Edc Identifier'
    identifier_prefix = '999'  # e.g. 066 for BHP066
    identifier_modulus = 7

    def ready(self):
        style = color_style()
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        if 'test' not in sys.argv:
            if self.identifier_prefix == '999':
                sys.stdout.write(style.NOTICE(
                    ' Warning: \'identifier_prefix\' has not been explicitly set. '
                    'Using default \'999\'. See AppConfig.\n'))
        sys.stdout.write(' * identifier prefix: {}\n'.format(self.identifier_prefix))
        sys.stdout.write(' * check-digit modulus: {}\n'.format(self.identifier_modulus))
        sys.stdout.write(' Done loading {} ...\n'.format(self.verbose_name))
