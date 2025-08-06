from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.dispatch import receiver
from edc_constants.constants import INCOMPLETE


@receiver(
    post_save, weak=False, dispatch_uid="update_subject_visit_document_status_on_pre_save"
)
def update_subject_visit_document_status_on_pre_save(
    instance, raw, using, update_fields, **kwargs
):
    """Updates the subject visit document status when an appointment
    is changed.

    Changing document status to incomplete forces the
    user to edit the subject visit on the dashboard
    before proceeding to the CRFs.
    """
    if not raw:
        try:
            subject_visit = getattr(instance, instance.related_visit_model_attr())
        except ObjectDoesNotExist:
            pass
        except AttributeError:
            pass
        else:
            if instance._meta.label_lower == "edc_appointment.appointment":
                old_instance = instance.__class__.objects.get(id=instance.id)
                if old_instance.appt_datetime.date() != instance.appt_datetime.date():
                    if subject_visit.document_status != INCOMPLETE:
                        subject_visit.document_status = INCOMPLETE
                        subject_visit.save_base(update_fields=["document_status"])
