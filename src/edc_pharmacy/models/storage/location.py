from django.db import models
from edc_model.models import BaseUuidModel, HistoricalRecords


class Manager(models.Manager):
    use_in_migrations = True


class Location(BaseUuidModel):

    name = models.CharField(max_length=50, unique=True)

    display_name = models.CharField(max_length=50, unique=True, null=True, blank=True)

    description = models.TextField(null=True)

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = self.name.capitalize()
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Location"
        verbose_name_plural = "Locations"
