from django.db import models
from django.db.models import get_app, get_models

# from edc_appointment.models import BaseAppointmentHelperModel

from ..managers import RegisteredSubjectManager

from .registered_subject import RegisteredSubject


# class BaseRegisteredSubjectModel (BaseAppointmentHelperModel):

class BaseRegisteredSubjectModel (models.Model):
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

    def get_visit_model_app(self):
        """Returns the app that contains the visit model for the
        RARE case where it is not in the same app as this model."""
        return None

    def get_visit_model_cls(self, instance=None):
        """Returns the visit model which is a subclass of :class:`BaseVisitTracking`."""
        from edc.subject.visit_tracking.models.base_visit_tracking import BaseVisitTracking
        if not instance:
            instance = self
        if instance.get_visit_model_app():
            app_label = instance.get_visit_model_app()
        else:
            app_label = instance._meta.app_label
        for model in get_models(get_app(app_label)):
            if isinstance(model(), BaseVisitTracking):
                return model
        raise TypeError(
            'Unable to determine the visit model for app {1} from instance {0}. '
            'Visit model and Off Study model are expected to be in the same app. '
            'If not use model method \'get_visit_model_app()\''.format(
                instance._meta.object_name, instance._meta.app_label))

    def get_visit_model(self, instance):
        """Returns the visit model which is a subclass of :class:`BaseVisitTracking`."""
        from edc.subject.visit_tracking.models.base_visit_tracking import BaseVisitTracking
        for model in get_models(get_app(instance._meta.app_label)):
            if isinstance(model(), BaseVisitTracking):
                return model
        raise TypeError(
            'Unable to determine the visit model from instance {0} for app {1}'.format(
                instance._meta.object_name, instance._meta.app_label))

    def get_registered_subject(self):
        return self.registered_subject

    class Meta:
        abstract = True
