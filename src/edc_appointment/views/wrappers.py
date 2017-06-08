from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.urls.base import reverse

from edc_model_wrapper import ModelWrapper


class AppointmentModelWrapper(ModelWrapper):

    visit_model_wrapper_cls = None

    model = django_apps.get_app_config('edc_appointment').model

    def get_appt_status_display(self):
        return self.object.get_appt_status_display()

    @property
    def title(self):
        return self.object.title

    @property
    def visit(self):
        """Returns a wrapped persistent or non-persistent visit instance."""
        try:
            return self.visit_model_wrapper_cls(model_obj=self.object.subjectvisit)
        except ObjectDoesNotExist:
            visit_model = self.visit_model_wrapper_cls.model
            return self.visit_model_wrapper_cls(
                model_obj=visit_model(
                    appointment=self.object,
                    subject_identifier=self.subject_identifier,))

    @property
    def forms_url(self):
        """Returns a reversed URL to show forms for this appointment/visit.

        This is standard for edc_dashboard"""
        kwargs = dict(
            subject_identifier=self.subject_identifier,
            appointment=self.object.id)
        return reverse(self.dashboard_url_name, kwargs=kwargs)
