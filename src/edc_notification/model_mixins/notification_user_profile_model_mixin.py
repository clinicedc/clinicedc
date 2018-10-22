from django.db import models

from ..models import Notification


class NotificationUserProfileModelMixin(models.Model):

    notifications = models.ManyToManyField(
        Notification,
        limit_choices_to={'enabled': True},
        blank=True)

    class Meta:
        abstract = True
