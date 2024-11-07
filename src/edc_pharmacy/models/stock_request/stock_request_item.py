from django.contrib.sites.models import Site
from django.db import models
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_randomization.site_randomizers import site_randomizers
from edc_utils import get_utcnow
from sequences import get_next_value

from ...utils import generate_code_with_checksum_from_id
from ..prescription import Rx
from .stock_request import StockRequest


class Manager(models.Manager):
    use_in_migrations = True


class StockRequestItem(BaseUuidModel):
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
    stock_request = models.ForeignKey(
        StockRequest, verbose_name="Stock request", on_delete=models.PROTECT
    )

    rx = models.ForeignKey(Rx, on_delete=models.PROTECT, null=True, blank=False)

    subject_identifier = models.CharField(max_length=15, null=True)

    sid = models.IntegerField(null=True)
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
            self.request_item_identifier = f"{next_id:06d}"
            self.code = generate_code_with_checksum_from_id(next_id)
        self.subject_identifier = self.rx.subject_identifier
        randomizer = site_randomizers.get(self.rx.randomizer_name)
        rando_obj = randomizer.model_cls().objects.get(
            subject_identifier=self.subject_identifier
        )
        self.sid = rando_obj.sid
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Stock request item"
        verbose_name_plural = "Stock request items"
