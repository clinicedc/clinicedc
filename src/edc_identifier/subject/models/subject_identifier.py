from django.db import models

from . import BaseIdentifierModel


class SubjectIdentifier(BaseIdentifierModel):

    objects = models.Manager()

    class Meta:
        app_label = 'edc_identifier'
        ordering = ['-created']
