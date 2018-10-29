from django.conf import settings
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from simple_history.signals import post_create_historical_record

from .site_notifications import site_notifications


@receiver(post_create_historical_record, weak=False,
          dispatch_uid='notification_on_post_create_historical_record')
def notification_on_post_create_historical_record(
        sender, instance, history_date, history_user,
        history_change_reason, **kwargs):
    if site_notifications.loaded:
        site_notifications.notify(
            instance=instance,
            user=instance.user_modified or instance.user_created,
            **kwargs)


@receiver(m2m_changed, weak=False,
          dispatch_uid='manage_mailists_on_userprofile_m2m_changed')
def manage_mailists_on_userprofile_m2m_changed(
        action, instance, reverse, model, pk_set, using, **kwargs):
    try:
        instance.notifications
    except AttributeError:
        pass
    else:
        if settings.EMAIL_ENABLED and site_notifications.loaded:
            if action == 'post_remove':
                for notification in instance.notifications.all():
                    notification_cls = site_notifications.get(
                        notification.name)
                    if notification_cls:
                        notification_cls().mailing_list_manager.unsubscribe(
                            instance.user, verbose=False)
            elif action == 'post_add':
                for notification in instance.notifications.all():
                    notification_cls = site_notifications.get(
                        notification.name)
                    if notification_cls:
                        notification_cls().mailing_list_manager.subscribe(
                            instance.user, verbose=False)
