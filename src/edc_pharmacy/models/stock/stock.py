from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from django.db import models
from django.db.models import PROTECT, DecimalField, ExpressionWrapper, F, QuerySet
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_sites.site import sites as site_sites
from edc_utils import get_utcnow
from sequences import get_next_value

from ...choices import STOCK_STATUS
from ...constants import AVAILABLE, RESERVED
from ...exceptions import InsufficientStockError
from ..stock_request import StockRequestItem
from .container import Container
from .location import Location
from .product import Product
from .receive_item import ReceiveItem
from .repack_request import RepackRequest

if TYPE_CHECKING:
    from ..medication import Assignment


class Manager(models.Manager):
    use_in_migrations = True

    def in_stock(
        self,
        unit_qty: Decimal,
        container: Container,
        location: Location,
        assignment: Assignment,
    ) -> QuerySet[Stock] | None:
        expression_wrapper = ExpressionWrapper(
            F("unit_qty_in") - F("unit_qty_out"),
            output_field=DecimalField(),
        )
        qs = (
            self.get_queryset()
            .filter(
                container=container,
                location=location,
                product__assignment=assignment,
                status=AVAILABLE,
            )
            .annotate(difference=expression_wrapper)
            .filter(difference__gte=unit_qty)
            .order_by("difference")
        )
        if qs.count() == 0:
            raise InsufficientStockError(
                f"Insufficient stock. Got container={container}, "
                f"location={location}, assignment={assignment}"
            )
        return qs[0]


class Stock(BaseUuidModel):

    stock_identifier = models.CharField(max_length=36, unique=True, null=True, blank=True)

    stock_datetime = models.DateTimeField(default=get_utcnow)

    receive_item = models.ForeignKey(
        ReceiveItem, on_delete=models.PROTECT, null=True, blank=False
    )

    repack_request = models.ForeignKey(
        RepackRequest, on_delete=models.PROTECT, null=True, blank=False
    )

    stock_request_item = models.ForeignKey(
        StockRequestItem, on_delete=models.PROTECT, null=True, blank=False
    )

    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    container = models.ForeignKey(Container, on_delete=models.PROTECT, null=True, blank=False)

    qty_in = models.DecimalField(
        null=True, blank=False, decimal_places=2, max_digits=20, default=Decimal(0.0)
    )

    qty_out = models.DecimalField(decimal_places=2, max_digits=20, default=Decimal(0.0))

    unit_qty_in = models.DecimalField(decimal_places=2, max_digits=20, default=Decimal(0.0))

    unit_qty_out = models.DecimalField(decimal_places=2, max_digits=20, default=Decimal(0.0))

    location = models.ForeignKey(Location, on_delete=PROTECT, null=True, blank=False)

    from_stock = models.ForeignKey(
        "edc_pharmacy.stock", related_name="source_stock", on_delete=models.PROTECT, null=True
    )

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

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.stock_identifier}:{self.description}"

    def save(self, *args, **kwargs):
        if not self.stock_identifier:
            next_id = get_next_value(self._meta.label_lower)
            self.stock_identifier = f"{next_id:06d}"
            self.product = self.get_receive_item().order_item.product
        if not self.description:
            self.description = f"{self.product.name} - {self.container.name}"
        if self.qty_out > self.qty_in:
            raise InsufficientStockError("QTY OUT cannot exceed QTY IN.")
        if self.stock_request_item:
            single_site = site_sites.get(self.stock_request_item.stock_request.site.id)
            if single_site.name != self.location.name:
                self.status = RESERVED
        super().save(*args, **kwargs)

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
