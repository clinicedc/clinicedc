from django.db import models

from . import BaseSequence


class Sequence(BaseSequence):

    objects = models.Manager()

    class Meta:
        app_label = 'edc_identifier'
        ordering = ['id', ]
