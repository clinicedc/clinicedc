from django.db import models
from django.utils import timezone


def timestamp():
    return timezone.now().strftime('%Y%m%d%H%M%S%f')


class ManifestModelMixin(models.Model):

    manifest_identifier = models.CharField(
        verbose_name='Manifest Identifier',
        default=timestamp,
        max_length=25,
        unique=True)

    manifest_datetime = models.DateTimeField(
        default=timezone.now)

    comment = models.TextField(
        verbose_name='Comment',
        null=True)

    shipped = models.BooleanField(default=False)

    class Meta:
        abstract = True
        ordering = ('-manifest_identifier', )
