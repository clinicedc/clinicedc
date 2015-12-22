from django.db import models

from .appointment import AppointmentHelper


class AppointmentMixin(models.Model):

    """ Model Mixin to add methods to create appointments.

    Such models may be listed by name in the ScheduledGroup model and thus
    trigger the creation of appointments.

    """

    def pre_prepare_appointments(self, using):
        """Users may override to add functionality before creating appointments."""
        return None

    def post_prepare_appointments(self, using):
        """Users may override to add functionality after creating appointments."""
        return None

    def prepare_appointments(self, using):
        """Creates all appointments linked to this instance.

        Calls :func:`pre_prepare_appointments` and :func:`post_prepare_appointments`.

        .. seealso:: :class:`appointment_helper.AppointmentHelper`. """
        self.pre_prepare_appointments(using)
        AppointmentHelper().create_all(self, using=using)
        self.post_prepare_appointments(using)

    class Meta:
        abstract = True
