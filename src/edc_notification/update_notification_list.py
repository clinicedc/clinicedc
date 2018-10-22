import sys

from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError

from .site_notifications import site_notifications


def update_notification_list(apps, verbose=False):
    Notification = apps.get_model('edc_notification', 'notification')
    if site_notifications.loaded:
        for name, notification_cls in site_notifications.registry.items():
            if verbose:
                sys.stdout.write(
                    f'{name}, {notification_cls().display_name}\n')
            try:
                obj = Notification.objects.get(name=name)
            except ObjectDoesNotExist:
                try:
                    Notification.objects.create(
                        name=name,
                        display_name=notification_cls().display_name)
                except IntegrityError as e:
                    raise IntegrityError(f'{e} Got name=\'{name}\'.')
            else:
                obj.display_name = notification_cls().display_name
                obj.save()
        names = list(site_notifications.registry)
        Notification.objects.exclude(name__in=names).update(enabled=False)
