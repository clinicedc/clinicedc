from django.db import models
from django.utils import timezone


class BaseIdentifierHistory(models.Model):

    identifier = models.CharField(
        max_length=25,
        unique=True
    )

    identifier_type = models.CharField(
        max_length=25,
    )

    identifier_prefix = models.CharField(
        max_length=25,
        null=True,
    )

    created_datetime = models.DateTimeField(
        default=timezone.now)

    class Meta:
        abstract = True


class IdentifierHistory(BaseIdentifierHistory):

    class Meta:
        app_label = 'edc_identifier'
