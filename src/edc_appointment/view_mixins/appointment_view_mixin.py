from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from ..constants import (
    CANCELLED_APPT,
    COMPLETE_APPT,
    IN_PROGRESS_APPT,
    INCOMPLETE_APPT,
    NEW_APPT,
)
from ..models import Appointment
from ..utils import update_unscheduled_appointment_sequence


class AppointmentViewMixin:

    """A view mixin to handle appointments on the dashboard."""

    appointment_model_wrapper_cls = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._appointment = None
        self._appointments = None
        self._wrapped_appointments = None
        self.appointment_model = "edc_appointment.appointment"
        self.appointment_id = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.appointment_id = kwargs.get("appointment")
        update_unscheduled_appointment_sequence(
            subject_identifier=self.kwargs.get("subject_identifier"),
        )
        has_call_manager = True if django_apps.app_configs.get("edc_call_manager") else False
        context.update(
            appointment=self.appointment_wrapped,
            appointments=self.appointments_wrapped,
            CANCELLED_APPT=CANCELLED_APPT,
            COMPLETE_APPT=COMPLETE_APPT,
            INCOMPLETE_APPT=INCOMPLETE_APPT,
            IN_PROGRESS_APPT=IN_PROGRESS_APPT,
            NEW_APPT=NEW_APPT,
            has_call_manager=has_call_manager,
        )
        return context

    @property
    def appointment_options(self):
        opts = {}
        if self.kwargs.get("appointment"):
            opts = dict(id=self.kwargs.get("appointment"))
        elif (
            self.kwargs.get("subject_identifier")
            and self.kwargs.get("visit_schedule_name")
            and self.kwargs.get("schedule_name")
            and self.kwargs.get("visit_code")
        ):
            visit_code_sequence = self.kwargs.get("visit_code_sequence") or 0
            opts = dict(
                subject_identifier=self.kwargs.get("subject_identifier"),
                visit_schedule_name=self.kwargs.get("visit_schedule_name"),
                schedule_name=self.kwargs.get("schedule_name"),
                visit_code=self.kwargs.get("visit_code"),
                visit_code_sequence=visit_code_sequence,
            )
        return opts

    @property
    def appointment(self):
        if not self._appointment:
            if self.appointment_id:
                try:
                    self._appointment = Appointment.on_site.get(id=self.appointment_id)
                except ObjectDoesNotExist:
                    opts = self.appointment_options
                    if opts:
                        try:
                            self._appointment = self.appointment_model_cls.on_site.get(**opts)
                        except ObjectDoesNotExist:
                            pass
        return self._appointment

    @property
    def appointment_wrapped(self):
        if self.appointment:
            return self.appointment_model_wrapper_cls(model_obj=self.appointment)
        return None

    @property
    def appointments(self):
        """Returns a Queryset of all appointments for this subject."""
        if not self._appointments:
            self._appointments = self.appointment_model_cls.on_site.filter(
                subject_identifier=self.subject_identifier
            ).order_by("timepoint", "visit_code_sequence")
        return self._appointments

    @property
    def appointments_wrapped(self):
        """Returns a list of wrapped appointments."""
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
