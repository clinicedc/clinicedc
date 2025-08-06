from django.db import models
from edc_model.models import BaseUuidModel


class Manager(models.Manager):
    use_in_migrations = True


class ScanDuplicates(BaseUuidModel):

    identifier = models.CharField(
        max_length=36,
        unique=True,
    )

    objects = Manager()

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Scan Duplicates"
        verbose_name_plural = "Scan Duplicates"
