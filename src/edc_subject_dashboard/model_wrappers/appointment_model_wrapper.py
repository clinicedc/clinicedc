from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.urls.base import reverse
from edc_model_wrapper import ModelWrapper


class AppointmentModelWrapperError(Exception):
    pass


class AppointmentModelWrapper(ModelWrapper):

    dashboard_url_name = settings.DASHBOARD_URL_NAMES.get(
        'subject_dashboard_url')
    next_url_name = settings.DASHBOARD_URL_NAMES.get('subject_dashboard_url')
    next_url_attrs = ['subject_identifier']
    querystring_attrs = ['subject_identifier', 'reason']
    unscheduled_appointment_url_name = 'edc_appointment:unscheduled_appointment_url'
    visit_model_wrapper_cls = None

    def __init__(self, model=None, **kwargs):
        if self.visit_model_wrapper_cls:
            declared_model = model or self.model
            model = django_apps.get_app_config(
                'edc_appointment').get_configuration(
                related_visit_model=self.visit_model_wrapper_cls.model).model
            if declared_model and model != declared_model:
                raise AppointmentModelWrapperError(
                    f'Declared model name does not match appointment '
                    f'model in visit_model_wrapper. Got self.model=\'{declared_model}\' '
                    f'!= {repr(self.visit_model_wrapper_cls)}.model=\'{model}\'. '
                    f'Try not explicitly declaring an appointment model if '
                    f'\'visit_model_wrapper_cls\' is declared. (e.g. leave cls.model = None).')

        super().__init__(model=model, **kwargs)

    def get_appt_status_display(self):
        return self.object.get_appt_status_display()

    @property
    def title(self):
        return self.object.title

    @property
    def visit_code_sequence(self):
        return self.object.visit_code_sequence

    @property
    def reason(self):
        return self.object.appt_reason

    @property
    def wrapped_visit(self):
        """Returns a wrapped persistent or non-persistent visit instance.
        """
        try:
            model_obj = self.object.subjectvisit
        except ObjectDoesNotExist:
            visit_model = django_apps.get_model(
                self.visit_model_wrapper_cls.model)
            model_obj = visit_model(
                appointment=self.object,
                subject_identifier=self.subject_identifier,
                reason=self.object.appt_reason)
        return self.visit_model_wrapper_cls(model_obj=model_obj)

    @property
    def forms_url(self):
        """Returns a reversed URL to show forms for this appointment/visit.

        This is standard for edc_dashboard.
        """
        kwargs = dict(
            subject_identifier=self.subject_identifier,
            appointment=self.object.id)
        return reverse(self.dashboard_url_name, kwargs=kwargs)

    @property
    def unscheduled_appointment_url(self):
        """Returns a url for the unscheduled appointment.
        """
        kwargs = dict(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.object.visit_schedule_name,
            schedule_name=self.object.schedule_name,
            visit_code=self.object.visit_code,
            redirect_url=self.dashboard_url_name)
        return reverse(self.unscheduled_appointment_url_name, kwargs=kwargs)
