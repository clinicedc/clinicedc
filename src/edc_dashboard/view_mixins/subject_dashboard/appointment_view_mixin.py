from django.apps import apps as django_apps

from edc_appointment.constants import NEW_APPT, IN_PROGRESS_APPT


class AppointmentViewMixin:

    """A view mixin to handle appointments on the dashboard.
    """

    reverse_relation_visit_attr_name = 'subjectvisit'
    appointment_model_wrapper_class = None
    visit_model_wrapper_class = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.appointment = None
        self._appointments = None

    def get(self, request, *args, **kwargs):
        try:
            appointment = self.appointment_model.objects.get(
                id=kwargs.get('appointment'))
        except self.appointment_model.DoesNotExist:
            self.appointment = None  # self.get_empty_appointment(**kwargs)
        else:
            self.appointment = self.appointment_model_wrapper_class(
                appointment)
        kwargs['appointment'] = self.appointment
        kwargs['appointments'] = self.appointments
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            NEW_APPT=NEW_APPT,
            IN_PROGRESS_APPT=IN_PROGRESS_APPT,
        )
        return context

    @property
    def appointments(self):
        """Returns a list of wrapped appointment instances.
        """
        if not self._appointments:
            appointments = self.appointment_model.objects.filter(
                subject_identifier=self.subject_identifier).order_by('visit_code')
            self._appointments = [
                self.appointment_model_wrapper_class(obj) for obj in appointments]
        return self._appointments

    @property
    def appointment_model(self):
        return django_apps.get_app_config('edc_appointment').model

    def empty_appointment(self, **kwargs):
        return self.appointment_model()
