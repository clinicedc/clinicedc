from django.contrib.sites.models import Site
from django.core.validators import RegexValidator
from django.db import models

from edc_list_data.model_mixins import ListModelMixin
from edc_model.models import BaseUuidModel, HistoricalRecords


class Manager(models.Manager):
    use_in_migrations = True


class Location(ListModelMixin, BaseUuidModel):
    display_name = models.CharField(
        verbose_name="Name",
        max_length=250,
        unique=True,
        null=True,
        blank=True,
        help_text="(suggest 40 characters max.)",
    )

    site = models.ForeignKey(Site, on_delete=models.PROTECT, null=True, blank=True)

    contact_name = models.CharField(max_length=150, default="", blank=True)
    contact_tel = models.CharField(
        max_length=150,
        validators=[RegexValidator("[0-9]{1,15}")],
        default="",
        blank=True,
    )
    contact_email = models.EmailField(max_length=150, default="", blank=True)

    objects = Manager()

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = self.name.capitalize()
        super().save(*args, **kwargs)

    class Meta(ListModelMixin.Meta, BaseUuidModel.Meta):
        verbose_name = "Location"
        verbose_name_plural = "Locations"
