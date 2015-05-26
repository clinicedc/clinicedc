# from django.db.models.signals import Signal, post_save

from edc.subject.registration.models import RegisteredSubject


class BaseAppointmentMixin(object):

    """ Mixin to add methods to a model that trigger the creation of appointments.

    It is better to access these methods through the BaseAppointmentHelperModel, which uses this mixin,  unless you cannot
    not following the same inheritance chain.

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
        from edc.subject.appointment_helper.classes import AppointmentHelper
        if 'registered_subject' in dir(self):
            registered_subject = self.registered_subject
        else:
            registered_subject = RegisteredSubject.objects.get(subject_identifier=self.subject_identifier)
        try:
            visit_definitions = self.get_visit_definitions_from_instance()
        except AttributeError:
            visit_definitions = None
        AppointmentHelper().create_all(
            registered_subject,
            self.__class__.__name__.lower(),
            using=using,
            source='BaseAppointmentMixin',
            visit_definitions=visit_definitions)
        self.post_prepare_appointments(using)
