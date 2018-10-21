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
            user=history_user,
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
        if site_notifications.loaded:
            if action == 'post_remove':
                for notification in instance.notifications.all():
                    notification_cls = site_notifications.get(
                        notification.name)
                    if not notification_cls:
                        notification.delete()
                    else:
                        notification_cls().mailing_list.unsubscribe(
                            instance.user.email)
            elif action == 'post_add':
                for notification in instance.notifications.all():
                    notification_cls = site_notifications.get(
                        notification.name)
                    if not notification_cls:
                        notification.delete()
                    else:
                        notification_cls().mailing_list.subscribe(
                            instance.user.email)


#         requests.post(
#             "https://api.mailgun.net/v3/lists/LIST@YOUR_DOMAIN_NAME/members",
#             auth=('api', 'YOUR_API_KEY'),
#             data={'subscribed': True,
#                   'address': 'bar@example.com',
#                   'name': 'Bob Bar',
#                   'description': 'Developer',
#                   'vars': '{"age": 26}'})
