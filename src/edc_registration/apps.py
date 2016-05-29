from django.apps import AppConfig


class EdcRegistrationAppConfig(AppConfig):
    name = 'edc_registration'
    verbose_name = 'Registration'

    def ready(self):
        pass
