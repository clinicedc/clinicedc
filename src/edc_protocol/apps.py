import sys

from django.apps import AppConfig as DjangoAppConfig

from django.core.exceptions import ImproperlyConfigured


class AppConfig(DjangoAppConfig):
    name = 'edc_protocol'
    verbose_name = 'Edc Protocol'

    protocol = 'BHP000'
    protocol_number = '000'
    protocol_name = 'My Protocol'
    protocol_title = 'My Protocol of Many Things'

    subject_types = ['subjects']
    enrollment_caps = {'subjects': -1}

    def ready(self):
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        for subject_type in self.subject_types:
            try:
                self.enrollment_caps[subject_type]
            except KeyError:
                raise ImproperlyConfigured(
                    'Expected an enrollment cap for subject_type \'{}\'. See AppConfig.'.format(subject_type))
        sys.stdout.write(' * {}: {}.\n'.format(self.protocol, self.protocol_name))
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))
