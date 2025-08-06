from django.db import models
from django_crypto_fields.fields import EncryptedCharField

from edc_model.models import BaseUuidModel, HistoricalRecords


class Manager(models.Manager):
    use_in_migrations = True


class Assignment(BaseUuidModel):

    name = EncryptedCharField(help_text="word as in randomization list")

    display_name = EncryptedCharField(
        verbose_name="Formal label",
        null=True,
        blank=True,
        help_text="If not provided, defaults to 'assignment'",
    )

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return self.display_name

    def save(self, *args, **kwargs):
        self.assignment = self.name.lower()
        if not self.display_name:
            self.display_name = self.assignment.title()
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Assignment"
        verbose_name_plural = "Assignments"
