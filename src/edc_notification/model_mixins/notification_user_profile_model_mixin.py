from django.db import models

from ..models import Notification


class NotificationUserProfileModelMixin(models.Model):

    email_notifications = models.ManyToManyField(
        Notification,
        related_name="email_notifications",
        limit_choices_to={"enabled": True},
        blank=True,
    )

    sms_notifications = models.ManyToManyField(
        Notification,
        related_name="sms_notifications",
        limit_choices_to={"enabled": True},
        blank=True,
    )

    class Meta:
        abstract = True
