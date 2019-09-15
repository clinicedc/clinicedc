from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch.dispatcher import receiver
from edc_constants.constants import YES, NO
from edc_utils import get_utcnow


@receiver(post_save, weak=False, dispatch_uid="update_ae_initial_for_susar")
def update_ae_initial_for_susar(sender, instance, raw, **kwargs):
    """Update AeInitial if SUSAR is created.
    """

    if not raw:
        try:
            submitted_datetime = instance.submitted_datetime
        except AttributeError:
            pass
        else:
            if submitted_datetime:
                if instance.ae_initial.susar_reported != YES:
                    instance.ae_initial.susar_reported = YES
                    instance.ae_initial.save(update_fields=["susar_reported"])
            elif instance.ae_initial.susar_reported != NO:
                instance.ae_initial.susar_reported = NO
                instance.ae_initial.save(update_fields=["susar_reported"])


@receiver(post_save, weak=False, dispatch_uid="update_ae_initial_susar_reported")
def update_ae_initial_susar_reported(sender, instance, raw, update_fields, **kwargs):
    """Create SUSAR instance if it does not already exist when
    Aeinitial.susar_reported == YES.
    """
    if not raw and not update_fields:
        if (
            instance._meta.label_lower
            == f"{settings.ADVERSE_EVENT_APP_LABEL}.aeinitial"
        ):
            if instance.susar_reported == YES:
                AeSusar = django_apps.get_model(
                    f"{settings.ADVERSE_EVENT_APP_LABEL}.aesusar"
                )
                try:
                    with transaction.atomic():
                        AeSusar.objects.get(ae_initial=instance)
                except ObjectDoesNotExist:
                    AeSusar.objects.create(
                        ae_initial=instance,
                        submitted_datetime=get_utcnow(),
                        subject_identifier=instance.subject_identifier,
                    )


@receiver(post_delete, weak=False, dispatch_uid="post_delete_ae_susar")
def post_delete_ae_susar(instance, **kwargs):
    if instance._meta.label_lower == f"{settings.ADVERSE_EVENT_APP_LABEL}.aesusar":
        if instance.aeinitial.susar_reported != NO:
            instance.susar_reported = NO
            instance.save()
