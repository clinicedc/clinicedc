from django.db.models import options

from ..appointment_creator import CreateAppointmentError
from .create_appointments_mixin import CreateAppointmentsMixin


if 'visit_schedule_name' not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('visit_schedule_name',)


class CreateAppointmentsOnEligibleMixin(CreateAppointmentsMixin):
    """Same as CreateAppointmentsMixin except will check for
    is_eligible=True before creating.
    """

    def create_appointments(self, base_appt_datetime=None):
        appointments = None
        try:
            if self.is_eligible:
                appointments = super().create_appointments(
                    base_appt_datetime)
        except AttributeError as e:
            if 'is_eligible' in str(e):
                raise CreateAppointmentError(str(e))
            raise AttributeError(str(e))
        return appointments

    class Meta:
        abstract = True
        visit_schedule_name = None
