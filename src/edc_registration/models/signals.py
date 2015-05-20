from django.db.models.signals import post_delete
from django.dispatch import receiver
from .base_registered_subject_model import BaseRegisteredSubjectModel


@receiver(post_delete, weak=False, dispatch_uid='delete_unused_appointments')
def delete_unused_appointments(sender, instance, **kwargs):
    """ Delete unused appointments linked to this instance on delete.

    This is an instance of a "membership" form """
    from edc.subject.appointment_helper.classes import AppointmentHelper
    if isinstance(instance, BaseRegisteredSubjectModel):
        AppointmentHelper().delete_for_instance(instance)
