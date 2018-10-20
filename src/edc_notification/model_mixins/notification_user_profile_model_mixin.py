from django.db import models

from ..models import Notification


class NotificationUserProfileModelMixin(models.Model):

    notifications = models.ManyToManyField(
        Notification,
        blank=True)

    class Meta:
        abstract = True
