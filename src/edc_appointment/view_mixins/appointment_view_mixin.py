from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.base import ContextMixin

from ..constants import (
    NEW_APPT,
    IN_PROGRESS_APPT,
    INCOMPLETE_APPT,
    COMPLETE_APPT,
    CANCELLED_APPT,
)


class AppointmentViewMixin(ContextMixin):

    """A view mixin to handle appointments on the dashboard.
    """

    appointment_model_wrapper_cls = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._appointments = None
        self._wrapped_appointments = None
        self.appointment_model = "edc_appointment.appointment"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            appointment=self.appointment_wrapped,
            appointments=self.appointments_wrapped,
            CANCELLED_APPT=CANCELLED_APPT,
            COMPLETE_APPT=COMPLETE_APPT,
            INCOMPLETE_APPT=INCOMPLETE_APPT,
            IN_PROGRESS_APPT=IN_PROGRESS_APPT,
            NEW_APPT=NEW_APPT,
        )
        return context

    @property
    def appointment(self):
        try:
            appointment = self.appointment_model_cls.objects.get(
                id=self.kwargs.get("appointment")
            )
        except ObjectDoesNotExist:
            appointment = None
        return appointment

    @property
    def appointment_wrapped(self):
        if self.appointment:
            return self.appointment_model_wrapper_cls(model_obj=self.appointment)
        return None

    @property
    def appointments(self):
        """Returns a Queryset of all appointments for this subject.
        """
        if not self._appointments:
            self._appointments = self.appointment_model_cls.objects.filter(
                subject_identifier=self.subject_identifier
            ).order_by("timepoint", "visit_code_sequence")
        return self._appointments

    @property
    def appointments_wrapped(self):
        """Returns a list of wrapped appointments.
        """
        if not self._wrapped_appointments:
            if self.appointments:
                wrapped = [
                    self.appointment_model_wrapper_cls(model_obj=obj)
                    for obj in self.appointments
                ]
                for i in range(0, len(wrapped)):
                    if wrapped[i].appt_status == IN_PROGRESS_APPT:
                        wrapped[i].disabled = False
                        for j in range(0, len(wrapped)):
                            if j != i:
                                wrapped[j].disabled = True
                self._wrapped_appointments = wrapped
        return self._wrapped_appointments or []

    @property
    def appointment_model_cls(self):
        return django_apps.get_model(self.appointment_model)

    def empty_appointment(self, **kwargs):
        return self.appointment_model_cls()
