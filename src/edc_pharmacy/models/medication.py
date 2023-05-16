from django.db import models
from edc_model import models as edc_models


class Manager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, name):
        return self.get(name)


class Medication(edc_models.BaseUuidModel):
    name = models.CharField(max_length=35, unique=True)

    display_name = models.CharField(max_length=50, unique=True)

    notes = models.TextField(max_length=250, null=True, blank=True)

    objects = Manager()

    history = edc_models.HistoricalRecords()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.strip().lower().replace(" ", "_")
        super().save(*args, **kwargs)

    def natural_key(self):
        return self.name

    class Meta(edc_models.BaseUuidModel.Meta):
        verbose_name = "Medication"
        verbose_name_plural = "Medications"
        unique_together = ["name", "display_name"]
