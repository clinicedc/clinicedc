import sys

from django.conf import settings
from django.db import models
from edc_base.model_mixins import BaseUuidModel


class Notification(BaseUuidModel):

    name = models.CharField(
        max_length=25,
        unique=True)

    display_name = models.CharField(
        max_length=255,
        unique=True)

    enabled = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.display_name}'

    class Meta:
        ordering = ('display_name', )


if settings.APP_NAME == 'edc_notification' and 'makemigrations' not in sys.argv:
    from .tests import models
