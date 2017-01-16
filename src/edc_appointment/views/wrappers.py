from django.apps import apps as django_apps

from edc_dashboard.wrappers import ModelWrapper


class AppointmentModelWrapper(ModelWrapper):

    model_name = django_apps.get_app_config('edc_appointment').model._meta.label_lower

    def add_extra_attributes_after(self):
        super().add_extra_attributes_after()
        self.title = self.wrapped_object.title
        self.get_appt_status_display = self.wrapped_object.get_appt_status_display
