from django.apps import apps as django_apps

from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = 'edc_registration'
    verbose_name = 'Registration'
    model_name = 'registeredsubject'
    app_label = None

    @property
    def model_class(self):
        return django_apps.get_model(self.app_label, self.model_name)
