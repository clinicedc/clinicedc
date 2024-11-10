from __future__ import annotations

from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import PROTECT
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_pylabels.models import LabelConfiguration
from edc_utils import get_utcnow
from sequences import get_next_value

from ...choices import STOCK_STATUS
from ...constants import ALLOCATED, AVAILABLE, ZERO_ITEM
from ...exceptions import StockError
from ...utils import get_random_code
from .allocation import Allocation
from .container import Container
from .location import Location
from .lot import Lot
from .managers import StockManager
from .product import Product
from .receive_item import ReceiveItem
from .repack_request import RepackRequest


class Stock(BaseUuidModel):

    stock_identifier = models.CharField(max_length=36, unique=True, null=True, blank=True)

    code = models.CharField(max_length=15, unique=True, null=True, blank=True)

    stock_datetime = models.DateTimeField(default=get_utcnow)

    receive_item = models.ForeignKey(
        ReceiveItem, on_delete=models.PROTECT, null=True, blank=False
    )

    repack_request = models.ForeignKey(
        RepackRequest, on_delete=models.PROTECT, null=True, blank=True
    )

    from_stock = models.ForeignKey(
        "edc_pharmacy.stock", related_name="source_stock", on_delete=models.PROTECT, null=True
    )

    allocation = models.ForeignKey(Allocation, on_delete=models.PROTECT, null=True, blank=True)

    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    container = models.ForeignKey(Container, on_delete=models.PROTECT, null=True, blank=False)

    qty_in = models.DecimalField(
        null=True,
        blank=False,
        decimal_places=2,
        max_digits=20,
        default=Decimal(0.0),
        validators=[MinValueValidator(0), MaxValueValidator(1)],
    )

    qty_out = models.DecimalField(
        decimal_places=2,
        max_digits=20,
        default=Decimal(0.0),
        validators=[MinValueValidator(0), MaxValueValidator(1)],
    )

    unit_qty_in = models.DecimalField(
        decimal_places=2,
        max_digits=20,
        default=Decimal(0.0),
        validators=[MinValueValidator(0)],
    )

    unit_qty_out = models.DecimalField(
        decimal_places=2,
        max_digits=20,
        default=Decimal(0.0),
        validators=[MinValueValidator(0)],
    )

    location = models.ForeignKey(Location, on_delete=PROTECT, null=True, blank=False)

    lot = models.ForeignKey(Lot, on_delete=models.PROTECT, null=True, blank=False)

    status = models.CharField(max_length=25, choices=STOCK_STATUS, default=AVAILABLE)

    description = models.CharField(max_length=100, null=True, blank=True)

    confirmed = models.BooleanField(default=False)
    confirmed_datetime = models.DateTimeField(null=True, blank=True)
    confirmed_by = models.CharField(
        max_length=150, null=True, blank=True, help_text="label_lower"
    )
    confirmed_by_identifier = models.CharField(max_length=36, null=True, blank=True)

    allocated_datetime = models.DateTimeField(null=True, blank=True)
    subject_identifier = models.CharField(max_length=50, null=True, blank=True)

    label_configuration = models.ForeignKey(
        LabelConfiguration, on_delete=models.PROTECT, null=True, blank=False
    )

    objects = StockManager()

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.stock_identifier}:{self.description}"

    def save(self, *args, **kwargs):
        if not self.stock_identifier:
            next_id = get_next_value(self._meta.label_lower)
            self.stock_identifier = f"{next_id:010d}"
            self.code = get_random_code(self.__class__, 6, 10000)
            self.product = self.get_receive_item().order_item.product
        if not self.description:
            self.description = f"{self.product.name} - {self.container.name}"
        # if not self.code:
        #     self.code = generate_code_with_checksum_from_id(int(self.stock_identifier))
        # if self.stock_request_item:
        #     single_site = site_sites.get(self.stock_request_item.stock_request.site.id)
        #     if single_site.name != self.location.name:
        #         self.status = RESERVED
        self.verify_assignment()
        self.verify_assignment(self.from_stock)
        self.verify_qty()
        self.update_status()
        super().save(*args, **kwargs)

    def verify_qty(self):
        if self.unit_qty_in > 0:
            if self.unit_qty_in == self.unit_qty_out:
                self.qty_out = 1
            else:
                self.qty_out = 0
            if self.qty_out > 1 or self.qty_in > 1:
                raise StockError("QTY OUT, QTY IN can only be 0 or 1.")

    def verify_assignment(self, stock: models.ForeignKey[Stock] | None = None):
        if not stock:
            stock = self
        if stock.product.assignment != stock.lot.assignment:
            raise StockError("Lot number assignment does not match product assignment!")

    def update_status(self):
        if self.allocation:
            self.status = ALLOCATED
        elif self.qty_out == self.qty_in:
            self.status = ZERO_ITEM
        else:
            self.status = AVAILABLE

    def get_receive_item(self) -> ReceiveItem:
        obj = self
        receive_item = self.receive_item
        while not receive_item:
            obj = obj.from_stock
            receive_item = obj.receive_item  # noqa
        return receive_item

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Stock"
        verbose_name_plural = "Stock"
