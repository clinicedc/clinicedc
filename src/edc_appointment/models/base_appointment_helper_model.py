from edc.subject.consent.models import BaseUuidModel

from .base_appointment_mixin import BaseAppointmentMixin


class BaseAppointmentHelperModel (BaseUuidModel, BaseAppointmentMixin):

    """ Base for models that may be trigger the creation of appointments such as registration models models that need a key to RegisteredSubject.

    Such models may be listed by name in the ScheduledGroup model and thus
    trigger the creation of appointments.

    """

    class Meta:
        abstract = True
