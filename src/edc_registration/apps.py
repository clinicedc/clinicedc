from django.apps import apps as django_apps

from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = 'edc_registration'
    verbose_name = 'Registration'
    model = None
    subject_types = ['subject']
    max_subjects = {'subject': -1}

    @property
    def model_class(self):
        return self.get_model(self.model[1])

    @property
    def registered_subject_model(self):
        return django_apps.get_model(*self.model)
