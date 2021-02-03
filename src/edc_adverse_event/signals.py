from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch.dispatcher import receiver
from edc_auth import TMG
from edc_constants.constants import NO, YES
from edc_notification.models import Notification
from edc_utils import get_utcnow

from edc_adverse_event.constants import DEATH_REPORT_TMG_ACTION

from .constants import AE_TMG_ACTION
from .get_ae_model import get_ae_model

AeInitial = get_ae_model("AeInitial")
AeSusar = get_ae_model("AeSusar")


@receiver(m2m_changed, weak=False, dispatch_uid="update_ae_notifications_for_tmg_group")
def update_ae_notifications_for_tmg_group(
    action, instance, reverse, model, pk_set, using, **kwargs
):

    try:
        instance.userprofile
    except AttributeError:
        pass
    else:
        try:
            tmg_ae_notification = Notification.objects.get(name=AE_TMG_ACTION)
        except ObjectDoesNotExist:
            pass
        else:
            try:
                with transaction.atomic():
                    instance.groups.get(name=TMG)
            except ObjectDoesNotExist:
                instance.userprofile.email_notifications.remove(tmg_ae_notification)
            else:
                instance.userprofile.email_notifications.add(tmg_ae_notification)


@receiver(post_save, sender=AeSusar, weak=False, dispatch_uid="update_ae_initial_for_susar")
def update_ae_initial_for_susar(sender, instance, raw, update_fields, **kwargs):
    if not raw and not update_fields:
        if instance.submitted_datetime:
            if instance.ae_initial.susar_reported != YES:
                instance.ae_initial.susar = YES
                instance.ae_initial.susar_reported = YES
                instance.ae_initial.save(update_fields=["susar", "susar_reported"])
        elif instance.ae_initial.susar_reported != NO:
            instance.ae_initial.susar = YES
            instance.ae_initial.susar_reported = NO
            instance.ae_initial.save(update_fields=["susar", "susar_reported"])


@receiver(
    post_save,
    sender=AeInitial,
    weak=False,
    dispatch_uid="update_ae_initial_susar_reported",
)
def update_ae_initial_susar_reported(sender, instance, raw, update_fields, **kwargs):
    if not raw and not update_fields:
        if instance.susar == YES and instance.susar_reported == YES:
            try:
                with transaction.atomic():
                    AeSusar.objects.get(ae_initial=instance)
            except ObjectDoesNotExist:
                AeSusar.objects.create(ae_initial=instance, submitted_datetime=get_utcnow())


@receiver(post_delete, sender=AeSusar, weak=False, dispatch_uid="post_delete_ae_susar")
def post_delete_ae_susar(instance, **kwargs):
    if instance.ae_initial.susar == YES and instance.ae_initial.susar_reported != NO:
        instance.ae_initial.susar_reported = NO
        instance.ae_initial.save()


@receiver(m2m_changed, weak=False, dispatch_uid="update_death_notifications_for_tmg_group")
def update_death_notifications_for_tmg_group(
    action, instance, reverse, model, pk_set, using, **kwargs
):

    try:
        instance.userprofile
    except AttributeError:
        pass
    else:
        try:
            tmg_death_notification = Notification.objects.get(name=DEATH_REPORT_TMG_ACTION)
        except ObjectDoesNotExist:
            pass
        else:
            try:
                instance.groups.get(name=TMG)
            except ObjectDoesNotExist:
                instance.userprofile.email_notifications.remove(tmg_death_notification)
            else:
                instance.userprofile.email_notifications.add(tmg_death_notification)
