from django.db import models
from django.db.models import UniqueConstraint
from edc_model.models import BaseUuidModel, HistoricalRecords


class Manager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, name):
        return self.get(name)


class Medication(BaseUuidModel):

    name = models.CharField(max_length=35, unique=True)

    display_name = models.CharField(max_length=50, unique=True)

    notes = models.TextField(max_length=250, null=True, blank=True)

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return self.display_name

    def save(self, *args, **kwargs):
        self.name = self.name.strip().lower().replace(" ", "_")
        if not self.display_name:
            self.display_name = self.name.capitalize()
        super().save(*args, **kwargs)

    def natural_key(self):
        return self.name

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Medication"
        verbose_name_plural = "Medications"
        constraints = [
            UniqueConstraint(
                fields=["name", "display_name"],
                name="%(app_label)s_%(class)s_name_uniq",
            )
        ]
