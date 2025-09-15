from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps

from .mailing_list_manager import MailingListManager
from .site_notifications import site_notifications
from .utils import get_email_enabled

if TYPE_CHECKING:
    from requests.models import Response

    from .models import Notification


def update_mailing_lists_in_m2m(
    sender=None,
    userprofile=None,
    pk_set=None,
    subscribe=None,
    unsubscribe=None,
    verbose=None,
    email_enabled=None,
) -> Response:
    """Update mailing list if email is enabled.

    See post-migrate signal:
        'manage_mailists_on_userprofile_m2m_changed'

    m2m_model = m2m model class for 'email_notifications' or
    'sms_notifications'.
    """
    response = None
    email_enabled = email_enabled or get_email_enabled()
    if (
        email_enabled
        and site_notifications.loaded
        and userprofile.email_notifications.through == sender
    ):
        notification_model_cls: type[Notification] = django_apps.get_model(
            "edc_notification.Notification"
        )
        for notification_obj in notification_model_cls.objects.filter(
            pk__in=list(pk_set), enabled=True
        ):
            notification_cls = site_notifications.get(notification_obj.name)
            notification = notification_cls()
            manager = MailingListManager(
                address=notification.email_to[0],
                display_name=notification.display_name,
                name=notification.name,
            )
            # response = manager.create(verbose=verbose)
            if subscribe:
                response = manager.subscribe(userprofile.user, verbose=verbose)
            elif unsubscribe:
                response = manager.unsubscribe(userprofile.user, verbose=verbose)
    return response
