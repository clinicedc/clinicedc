import requests

from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from .site_notifications import site_notifications


@receiver(post_save, weak=False, dispatch_uid='notification_on_post_save')
def notification_on_post_save(sender, instance, raw,
                              created, update_fields, **kwargs):
    if not raw and not update_fields:
        if site_notifications.loaded:
            site_notifications.notify(
                sender=sender,
                instance=instance,
                created=created,
                **kwargs)


@receiver(m2m_changed, weak=False, dispatch_uid='manage_mailists_on_userprofile_m2m_changed')
def manage_mailists_on_userprofile_m2m_changed(
        action, instance, reverse, model, pk_set, using, **kwargs):
    if action == 'post_add' and site_notifications.loaded:
        print(action, instance, reverse, model, pk_set, using)
        try:
            notifications = instance.notifications.all()
        except AttributeError:
            pass
        else:
            for notification in notifications:
                if notification.enabled:
                    notification_cls = site_notifications.get(
                        notification.name)
                    print(notification_cls)
#         requests.post(
#             "https://api.mailgun.net/v3/lists/LIST@YOUR_DOMAIN_NAME/members",
#             auth=('api', 'YOUR_API_KEY'),
#             data={'subscribed': True,
#                   'address': 'bar@example.com',
#                   'name': 'Bob Bar',
#                   'description': 'Developer',
#                   'vars': '{"age": 26}'})
