from django.apps import AppConfig


class EdcRegistrationAppConfig(AppConfig):
    name = 'edc_registration'
    verbose_name = 'Registration'
    model = None

    @property
    def model_class(self):
        return self.get_model(self.model[1])
