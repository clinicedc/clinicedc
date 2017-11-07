from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from ..constants import (
    NEW_APPT, IN_PROGRESS_APPT, INCOMPLETE_APPT, COMPLETE_APPT)


class AppointmentViewMixin:

    """A view mixin to handle appointments on the dashboard.
    """

    reverse_relation_visit_attr_name = 'subjectvisit'
    appointment_model_wrapper_cls = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._appointments = None
        self.appointment_model = self.appointment_model_wrapper_cls.model

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            appointment=self.appointment_wrapped,
            appointments=self.appointments_wrapped,
            NEW_APPT=NEW_APPT,
            INCOMPLETE_APPT=INCOMPLETE_APPT,
            COMPLETE_APPT=COMPLETE_APPT,
            IN_PROGRESS_APPT=IN_PROGRESS_APPT)
        return context

    @property
    def appointment(self):
        try:
            appointment = self.appointment_model_cls.objects.get(
                id=self.kwargs.get('appointment'))
        except ObjectDoesNotExist:
            appointment = None
        return appointment

    @property
    def appointment_wrapped(self):
        if self.appointment:
            return self.appointment_model_wrapper_cls(
                self.appointment)
        return None

    @property
    def appointments(self):
        """Returns a Queryset of all appointments for this subject.
        """
        if not self._appointments:
            self._appointments = self.appointment_model_cls.objects.filter(
                subject_identifier=self.subject_identifier).order_by(
                    'timepoint_datetime')
        return self._appointments

    @property
    def appointments_wrapped(self):
        """Returns a list of wrapped appointments.
        """
        appointments = []
        if self.appointments:
            appointments = [
                self.appointment_model_wrapper_cls(obj) for obj in self.appointments]
            for i in range(0, len(appointments)):
                if appointments[i].appt_status == IN_PROGRESS_APPT:
                    appointments[i].disabled = False
                    for j in range(0, len(appointments)):
                        if j != i:
                            appointments[j].disabled = True
        return appointments

    @property
    def appointment_model_cls(self):
        return django_apps.get_app_config(self.appointment_model).model

    def empty_appointment(self, **kwargs):
        return self.appointment_model_cls()
