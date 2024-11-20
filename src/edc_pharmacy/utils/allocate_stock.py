from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_utils import get_utcnow

from ..exceptions import AllocationError

if TYPE_CHECKING:
    from ..models import StockRequest


def allocate_stock(
    stock_request: StockRequest,
    allocation_data: dict[str, str],
    allocated_by: str,
    user_created: str = None,
    created: datetime = None,
) -> tuple[int, int]:
    stock_model_cls = django_apps.get_model("edc_pharmacy.stock")
    allocation_model_cls = django_apps.get_model("edc_pharmacy.allocation")
    registered_subject_model_cls = django_apps.get_model("edc_registration.registeredsubject")
    allocated, unallocated = 0, 0
    stock_objs = []
    for code, subject_identifier in allocation_data.items():
        rs_obj = registered_subject_model_cls.objects.get(
            subject_identifier=subject_identifier
        )
        stock_request_item = stock_request.stockrequestitem_set.filter(
            registered_subject=rs_obj,
            allocation__isnull=True,
        ).first()
        if not stock_request_item:
            unallocated += 1
            continue
        try:
            stock_obj = stock_model_cls.objects.get(code=code, allocation__isnull=True)
        except ObjectDoesNotExist:
            unallocated += 1
        else:
            allocation = allocation_model_cls.objects.create(
                stock_request_item=stock_request_item,
                registered_subject=rs_obj,
                allocation_datetime=get_utcnow(),
                allocated_by=allocated_by,
                user_created=user_created,
                created=created,
            )
            if (
                stock_model_cls.objects.get(code=code).product.assignment
                != allocation.get_assignment()
            ):
                allocation.delete()
                raise AllocationError(
                    "Assignment mismatch. Stock must match subject assignment. "
                    "Allocation abandoned."
                )

            stock_obj.allocation = allocation
            stock_obj.user_modified = user_created
            stock_obj.modified = created
            stock_objs.append(stock_obj)
    if stock_objs:
        for obj in stock_objs:
            obj.save()
            allocated += 1
    return allocated, unallocated
