from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from simple_history.signals import post_create_historical_record

from .update_mailing_lists_in_m2m import update_mailing_lists_in_m2m
from .site_notifications import site_notifications


@receiver(
    post_create_historical_record,
    weak=False,
    dispatch_uid="notification_on_post_create_historical_record",
)
def notification_on_post_create_historical_record(
    instance, history_date, history_user, history_change_reason, **kwargs
):
    """Checks and processes any notifications for this model.

    Processes if `label_lower` is in site_notifications.models.

    Note, this is the post_create of the historical model.
    """
    if (
        site_notifications.loaded
        and instance._meta.label_lower in site_notifications.models
    ):
        opts = dict(
            instance=instance,
            user=instance.user_modified or instance.user_created,
            history_date=history_date,
            history_user=history_user,
            history_change_reason=history_change_reason,
            fail_silently=True,
            **kwargs
        )
        site_notifications.notify(**opts)


@receiver(
    m2m_changed, weak=False, dispatch_uid="manage_mailists_on_userprofile_m2m_changed"
)
def manage_mailists_on_userprofile_m2m_changed(
    action, instance, pk_set, sender, **kwargs
):
    """Updates the mail server mailing lists based on the
    selections in the UserProfile model.
    """
    try:
        instance.email_notifications
    except AttributeError:
        pass
    else:
        if action == "post_remove":
            update_mailing_lists_in_m2m(
                sender=sender,
                userprofile=instance,
                unsubscribe=True,
                pk_set=pk_set,
                verbose=True,
            )
        elif action == "post_add":
            update_mailing_lists_in_m2m(
                sender=sender,
                userprofile=instance,
                subscribe=True,
                pk_set=pk_set,
                verbose=True,
            )
