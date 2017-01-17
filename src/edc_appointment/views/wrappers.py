from django.apps import apps as django_apps

from edc_dashboard.wrappers import ModelWrapper
from django.core.exceptions import ObjectDoesNotExist
from django.urls.base import reverse


class AppointmentModelWrapper(ModelWrapper):

    model_name = django_apps.get_app_config('edc_appointment').model._meta.label_lower

    def add_extra_attributes_after(self):
        super().add_extra_attributes_after()
        self.get_appt_status_display = self.wrapped_object.get_appt_status_display

    @property
    def title(self):
        return self.wrapped_object.title

    @property
    def visit(self):
        """Returns a wrapped persistent or non-persistent visit instance."""
        try:
            return self.visit_model_wrapper_class(self._original_object.subjectvisit)
        except ObjectDoesNotExist:
            visit_model = django_apps.get_model(
                *self.visit_model_wrapper_class.model_name.split('.'))
            print(self.survey_schedule_object, self, self.survey)
            return self.visit_model_wrapper_class(
                visit_model(appointment=self._original_object))

    @property
    def forms_url(self):
        """Returns a reversed URL to show forms for this appointment/visit.

        This is standard for edc_dashboard"""
        kwargs = dict(
            subject_identifier=self.subject_identifier,
            appointment=self.wrapped_object.id)
        return reverse(self.dashboard_url_name, kwargs=kwargs)
