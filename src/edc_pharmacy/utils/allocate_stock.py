from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone

from ..exceptions import AllocationError

if TYPE_CHECKING:
    from ..models import StockRequest


def allocate_stock(
    stock_request: StockRequest,
    allocation_data: dict[str, str],
    allocated_by: str,
    user_created: str = None,
    created: datetime = None,
) -> tuple[list[int], list[str]]:
    """Link stock instances to subjects.

    Model `Allocation` is a fkey on Stock and links the stock obj to a
    subject.

    allocation_data: dict of {stock code:subject_identifier} coming from
    the view.

    for any stock instance, the container must be a container used for
    subjects, e.g. bottle 128. That is container__may_request_as=True.

    See post() in AllocateToSubjectView.
    """
    stock_model_cls = django_apps.get_model("edc_pharmacy.stock")
    allocation_model_cls = django_apps.get_model("edc_pharmacy.allocation")
    registered_subject_model_cls = django_apps.get_model("edc_registration.registeredsubject")
    allocated, skipped = [], []
    stock_objs = []
    for code, subject_identifier in allocation_data.items():
        # get rs
        rs_obj = registered_subject_model_cls.objects.get(
            subject_identifier=subject_identifier
        )
        # get the stock request item from this request for this subject
        stock_request_item = stock_request.stockrequestitem_set.filter(
            registered_subject=rs_obj,
            allocation__isnull=True,
        ).first()
        if not stock_request_item:
            skipped.append(f"{subject_identifier}: N/A")
            continue
        # try to create the allocation instance and update the stock instance
        # for this stock code
        try:
            stock_obj = stock_model_cls.objects.get(
                code=code,
                confirmation__isnull=False,
                container__may_request_as=True,
                allocation__isnull=True,
            )
        except ObjectDoesNotExist:
            skipped.append(f"{subject_identifier}: {code}")
        else:
            with transaction.atomic():
                allocation = allocation_model_cls.objects.create(
                    stock_request_item=stock_request_item,
                    registered_subject=rs_obj,
                    allocation_datetime=timezone.now(),
                    allocated_by=allocated_by,
                    user_created=user_created,
                    created=created,
                )
                # check stock assigment matches subject`s assignment
                if (
                    stock_model_cls.objects.get(code=code).product.assignment
                    != allocation.get_assignment()
                ):
                    allocation.delete()
                    raise AllocationError(
                        "Assignment mismatch. Stock must match subject assignment. "
                        f"Allocation abandoned. See {subject_identifier} and {stock_obj}."
                    )

                stock_obj.allocation = allocation
                stock_obj.allocated = True
                stock_obj.user_modified = user_created
                stock_obj.modified = created
                stock_objs.append(stock_obj)
    if stock_objs:
        for obj in stock_objs:
            obj.save()
            allocated.append(obj.code)
    return allocated, skipped


__all__ = ["allocate_stock"]
