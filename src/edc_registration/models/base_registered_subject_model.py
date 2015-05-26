from django.db import models

from edc_base.model.models import BaseUuidModel

from ..managers import RegisteredSubjectManager

from .registered_subject import RegisteredSubject


class BaseRegisteredSubjectModel (BaseUuidModel):
    """ Base model for models that need a key to RegisteredSubject.

    Such models may be listed by name in the ScheduledGroup model and thus
    trigger the creation of appointments. Other instances may be Additional
    forms which are link to a subject but not a time point (for example,
    a Death model or OffStudy model (see also AdditionalEntryBucket)

    Use this along with BaseRegisteredSubjectModelAdmin()

    .. seealso:: This class inherits methods from edc.subject.appointment_helper
        that create appointments if the model
        is configured as a ScheduledGroup model. See base
        class :mod:`bhp_appointment_helper.classes.BaseAppointmentHelperModel`.

    """
    registered_subject = models.OneToOneField(RegisteredSubject)

    objects = RegisteredSubjectManager()

    def __str__(self):
        return str(self.registered_subject)

    def natural_key(self):
        return self.registered_subject.natural_key()
    natural_key.dependencies = ['registration.registeredsubject']

    def get_subject_identifier(self):
        """Returns the subject_identifier."""
        return self.registered_subject.subject_identifier

    def get_registered_subject(self):
        return self.registered_subject

    class Meta:
        abstract = True
