import sys

from django.apps import apps as django_apps

from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = 'edc_registration'
    verbose_name = 'Edc Registration'
    app_label = 'edc_registration'

    def ready(self):
        from .signals import update_registered_subject_from_model_on_post_save
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        sys.stdout.write('  * using {}.registeredsubject\n'.format(self.app_label, ))
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))

    @property
    def model(self):
        return django_apps.get_model(self.app_label, 'registeredsubject')
