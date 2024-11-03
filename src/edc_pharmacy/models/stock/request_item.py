from django.contrib.sites.models import Site
from django.db import models
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_utils import get_utcnow
from sequences import get_next_value

from ...utils import generate_code_with_checksum_from_id
from .request import Request


class Manager(models.Manager):
    use_in_migrations = True


class RequestItem(BaseUuidModel):
    """A model that represents a stock request item.

    At this time the Stock container must be a subject
    specific container

    A stock label is created from the request linked
    to the stock table
    """

    request_item_identifier = models.CharField(
        max_length=36, unique=True, null=True, blank=True
    )
    code = models.CharField(max_length=15, unique=True, help_text="Human readable code")

    request_item_datetime = models.DateTimeField(default=get_utcnow)
    request = models.ForeignKey(
        Request, verbose_name="Stock request", on_delete=models.PROTECT
    )

    subject_identifier = models.CharField(max_length=15, null=True)

    sid = models.IntegerField(
        null=True,
        help_text="Pharmacy reference for rando assignment. Validated against the Stock FK",
    )
    site = models.ForeignKey(Site, null=True, on_delete=models.PROTECT)

    gender = models.CharField(max_length=5, null=True, help_text="Add for convenience")

    printed_datetime = models.DateTimeField(null=True)
    printed = models.BooleanField(default=False)

    scanned_datetime = models.DateTimeField(null=True)
    scanned = models.BooleanField(default=False)

    received_datetime = models.DateTimeField(null=True)
    received = models.BooleanField(default=False, help_text="Received at site")

    dispensed_datetime = models.DateTimeField(null=True)
    dispensed = models.BooleanField(default=False, help_text="Dispensed to clinic")

    crf_datetime = models.DateTimeField(null=True)
    crf = models.BooleanField(default=False, help_text="Entered into subject's CRF")

    objects = Manager()

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if not self.request_item_identifier:
            next_id = get_next_value(self._meta.label_lower)
            self.request_item_identifier = next_id
            self.code = generate_code_with_checksum_from_id(next_id)
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Stock: Request item"
        verbose_name_plural = "Stock: Request items"
