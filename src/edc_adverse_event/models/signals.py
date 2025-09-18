from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch.dispatcher import receiver
from django.utils import timezone

from edc_constants.constants import NO, YES
from edc_notification.models import Notification

from ..constants import AE_TMG_ACTION, DEATH_REPORT_TMG_ACTION, TMG
from ..utils import get_ae_model


@receiver(m2m_changed, weak=False, dispatch_uid="update_ae_notifications_for_tmg_group")
def update_ae_notifications_for_tmg_group(action, instance, **kwargs):
    if getattr(instance, "userprofile", None):
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


@receiver(post_save, weak=False, dispatch_uid="update_ae_initial_for_susar")
def update_ae_initial_for_susar(sender, instance, raw, update_fields, **kwargs):
    if not raw and not update_fields:
        try:
            ae_susar_model_cls = get_ae_model("AeSusar")
        except LookupError:
            pass
        else:
            if isinstance(instance, (ae_susar_model_cls,)) and getattr(
                instance.ae_initial, "susar", None
            ):
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
    weak=False,
    dispatch_uid="update_ae_initial_susar_reported",
)
def update_ae_initial_susar_reported(sender, instance, raw, update_fields, **kwargs):
    if not raw and not update_fields:
        try:
            ae_initial_model_cls = get_ae_model("AeInitial")
        except LookupError:
            pass
        else:
            if isinstance(instance, (ae_initial_model_cls,)) and getattr(
                instance, "susar", None
            ):
                ae_susar_model_cls = get_ae_model("AeSusar")
                if instance.susar == YES and instance.susar_reported == YES:
                    try:
                        with transaction.atomic():
                            ae_susar_model_cls.objects.get(ae_initial=instance)
                    except ObjectDoesNotExist:
                        ae_susar_model_cls.objects.create(
                            ae_initial=instance, submitted_datetime=timezone.now()
                        )


@receiver(post_delete, weak=False, dispatch_uid="post_delete_ae_susar")
def post_delete_ae_susar(instance, **kwargs):
    try:
        ae_susar_model_cls = get_ae_model("AeSusar")
    except LookupError:
        pass
    else:
        if (
            isinstance(instance, (ae_susar_model_cls,))
            and instance.ae_initial.susar == YES
            and instance.ae_initial.susar_reported != NO
        ):
            instance.ae_initial.susar_reported = NO
            instance.ae_initial.save()


@receiver(m2m_changed, weak=False, dispatch_uid="update_death_notifications_for_tmg_group")
def update_death_notifications_for_tmg_group(action, instance, **kwargs):
    if getattr(instance, "userprofile", None):
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
