from django.core.exceptions import ObjectDoesNotExist

from .site_notifications import site_notifications


def update_notification_list(apps):
    Notification = apps.get_model('edc_notification', 'notification')
    for name, notification_cls in site_notifications.registry.items():
        try:
            obj = Notification.objects.get(name=name)
        except ObjectDoesNotExist:
            Notification.objects.create(
                name=name, display_name=notification_cls.display_name)
        else:
            obj.display_name = notification_cls.display_name
            obj.save()
