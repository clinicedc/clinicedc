from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured


class EnrollmentModel:

    def __init__(self, model=None, app_label=None, model_name=None, visible=None):
        if model:
            self.model = model
            self.app_label = model._meta.app_label
            self.model_name = model._meta.model_name
        else:
            self.app_label = app_label
            self.model_name = model_name
            self.model = django_apps.get_model(self.app_label, self.model_name)
        self.visible = True if visible is None else visible
        self.name = '{}.{}'.format(self.app_label, self.model_name)
        try:
            self.prepare_appointments
        except AttributeError:
            raise ImproperlyConfigured(
                'EnrollmentModel missing required method \'prepare_appointments\'. '
                'See edc_appointment.CreateAppointmentsMixin. Got {0}'.format(self.model))

    def __repr__(self):
        return 'EnrollmentModel({}, {}, {})'.format(self.app_label, self.model_name, self.visible)

    def __str__(self):
        return self.model._meta.verbose_name

    @property
    def category(self):
        return self.name
