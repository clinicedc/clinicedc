from django.db import models
from django.utils import timezone
from sequences import get_next_value

from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_sites.model_mixins import SiteModelMixin

from ..prescription import Rx
from .location import Location


class Manager(models.Manager):
    use_in_migrations = True


class Dispense(SiteModelMixin, BaseUuidModel):
    dispense_identifier = models.CharField(
        max_length=36,
        unique=True,
        null=True,
        blank=True,
        help_text="A sequential unique identifier set by the EDC",
    )

    dispense_datetime = models.DateTimeField(default=timezone.now)

    dispensed_by = models.CharField(max_length=100, default="", blank=True)

    rx = models.ForeignKey(Rx, on_delete=models.PROTECT, null=True, blank=False)

    location = models.ForeignKey(Location, on_delete=models.PROTECT, null=True, blank=False)

    to_clinician = models.BooleanField(default=False)
    to_clinician_datetime = models.DateTimeField(null=True, blank=True)

    to_subject = models.BooleanField(default=False)
    to_subject_datetime = models.DateTimeField(null=True, blank=True)
    crf_label_lower = models.CharField(max_length=100, default="", blank=True)
    crf_field_name = models.CharField(max_length=100, default="", blank=True)
    crf_id = models.UUIDField(null=True, blank=True)

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return self.dispense_identifier

    def save(self, *args, **kwargs):
        self.site = self.location.site
        if not self.dispense_identifier:
            self.dispense_identifier = f"{get_next_value(self._meta.label_lower):06d}"
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Dispense"
        verbose_name_plural = "Dispense"
