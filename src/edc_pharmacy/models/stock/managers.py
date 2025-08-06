from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from django.db import models
from django.db.models import DecimalField, ExpressionWrapper, F, QuerySet

from ...constants import AVAILABLE
from ...exceptions import InsufficientStockError
from ..medication import Assignment
from .container import Container
from .location import Location

if TYPE_CHECKING:
    from .stock import Stock


class StockManager(models.Manager):
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
