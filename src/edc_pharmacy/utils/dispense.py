from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest

from ..constants import TXN_DISPENSED
from ..exceptions import InvalidTransitionError
from ..transaction_log import apply_transaction

if TYPE_CHECKING:
    from ..models import Dispense, Location, Stock


def dispense(
    stock_codes: list[str],
    location: Location,
    rx,
    dispensed_by: str,
    request: WSGIRequest,
) -> tuple[list[str], list[str], list[str]]:
    """Dispense scanned stock to a subject.

    Returns ``(dispensed, already_dispensed, invalid)``.

    Safety policy (Option C):
        - not-found codes are reported in ``invalid`` but do NOT abort the
          batch (likely scan glitch / foreign barcode).
        - unallocated stock, subject mismatch, and site mismatch are
          clinical-safety violations and abort the entire batch — no
          Dispense parent or DispenseItem rows are written.
        - already-dispensed (caught from apply_transaction) is reported
          in ``already_dispensed``.
    """
    stock_model_cls: type[Stock] = django_apps.get_model("edc_pharmacy.stock")
    dispense_model_cls: type[Dispense] = django_apps.get_model("edc_pharmacy.dispense")

    dispensed: list[str] = []
    already_dispensed: list[str] = []
    invalid: list[str] = []

    stock_codes = [c.strip() for c in (stock_codes or [])]

    # Phase 1: pre-flight safety check across the whole batch.
    stocks_in_batch = list(stock_model_cls.objects.filter(code__in=stock_codes))
    found = {s.code for s in stocks_in_batch}

    # Not-found: report but do not abort.
    for code in stock_codes:
        if code not in found:
            messages.add_message(
                request,
                messages.ERROR,
                f"Stock {code} not found. Skipped.",
            )
            invalid.append(code)

    # Safety-critical checks: any failure aborts the entire batch.
    abort_batch = False
    for stock in stocks_in_batch:
        allocation = stock.allocation
        rs = getattr(allocation, "registered_subject", None) if allocation else None
        if allocation is None or rs is None:
            messages.add_message(
                request,
                messages.ERROR,
                f"Stock {stock.code} is not allocated. Dispensing cancelled.",
            )
            invalid.append(stock.code)
            abort_batch = True
            continue
        if rs.subject_identifier != rx.subject_identifier:
            messages.add_message(
                request,
                messages.ERROR,
                f"Stock not allocated to subject. Got {stock.code}. "
                "Dispensing cancelled.",
            )
            invalid.append(stock.code)
            abort_batch = True
            continue
        if stock.location is None or rs.site_id != stock.location.site_id:
            messages.add_message(
                request,
                messages.ERROR,
                (
                    "Stock location does not match subject's site. "
                    f"Stock item {stock.code} not at site {rs.site_id}. "
                    "Dispensing cancelled."
                ),
            )
            invalid.append(stock.code)
            abort_batch = True
            continue

    if abort_batch:
        # Whole-batch abort — no Dispense parent, no items.
        return dispensed, already_dispensed, invalid

    # Phase 2: per-code apply_transaction. Only the safety-clean codes from
    # stocks_in_batch reach here. Not-found codes are already in ``invalid``
    # but Phase 2 proceeds for the rest.
    if not stocks_in_batch:
        return dispensed, already_dispensed, invalid

    dispense_obj = dispense_model_cls.objects.create(
        rx=rx, location=location, dispensed_by=dispensed_by
    )
    for stock in stocks_in_batch:
        try:
            apply_transaction(stock, TXN_DISPENSED, request.user, dispense=dispense_obj)
        except InvalidTransitionError:
            messages.add_message(
                request,
                messages.ERROR,
                f"Stock already dispensed. Got {stock.code}.",
            )
            already_dispensed.append(stock.code)
        else:
            dispensed.append(stock.code)

    return dispensed, already_dispensed, invalid


__all__ = ["dispense"]
