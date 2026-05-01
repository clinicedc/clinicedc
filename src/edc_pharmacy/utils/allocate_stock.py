from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone

from ..constants import TXN_ALLOCATED
from ..exceptions import AllocationError
from ..transaction_log import apply_transaction

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

    from ..models import Stock, StockRequest


def allocate_stock(
    stock_request: StockRequest,
    allocation_data: dict[str, str],
    allocated_by: str,
    user_created: str | None = None,
    created=None,
    actor: AbstractUser | None = None,
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
    for code, subject_identifier in allocation_data.items():
        rs_obj = registered_subject_model_cls.objects.get(
            subject_identifier=subject_identifier
        )
        stock_request_item = stock_request.stockrequestitem_set.filter(
            registered_subject=rs_obj,
            allocation__isnull=True,
        ).first()
        if not stock_request_item:
            skipped.append(f"{subject_identifier}: N/A")
            continue
        with transaction.atomic():
            # Lock the stock row before checking current_allocation.
            try:
                stock_obj: Stock = stock_model_cls.objects.select_for_update(of=("self",)).get(
                    code=code,
                    confirmation__isnull=False,
                    container__may_request_as=True,
                    current_allocation__isnull=True,
                )
            except ObjectDoesNotExist:
                skipped.append(f"{subject_identifier}: {code}")
            else:
                allocation = allocation_model_cls.objects.create(
                    stock_request_item=stock_request_item,
                    code=stock_obj.code,
                    registered_subject=rs_obj,
                    allocation_datetime=timezone.now(),
                    allocated_by=allocated_by,
                    user_created=user_created,
                    created=created or timezone.now(),
                )
                if stock_obj.product.assignment != allocation.assignment:
                    raise AllocationError(
                        "Assignment mismatch. Stock must match subject assignment. "
                        f"Allocation abandoned. See {subject_identifier} and {stock_obj}."
                    )
                apply_transaction(
                    stock_obj,
                    TXN_ALLOCATED,
                    actor,
                    allocation=allocation,
                    registered_subject=rs_obj,
                    stock_request_item=stock_request_item,
                    allocated_by=allocated_by,
                )
                allocated.append(code)
    return allocated, skipped


__all__ = ["allocate_stock"]
