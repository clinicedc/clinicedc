"""Cross-bin conflict annotation for stock take discrepancies.

Shared by the discrepancy report and the results page so both render the same
hints and the same missing-item resolution choice (lost vs acknowledge).
"""

from __future__ import annotations

from collections.abc import Iterable

from django.db.models import Exists, OuterRef, QuerySet

from edc_utils.date import to_local

from ..models import MISSING, UNEXPECTED, StockTake, StockTakeItem, StorageBinItem


def open_discrepancies(codes: Iterable[str], statuses: Iterable[str]) -> QuerySet:
    """Open discrepancies for the given codes/statuses, latest take per bin only.

    "Open" = unresolved (no ``stock_transaction``) and not acknowledged. Items
    belonging to a superseded (older) stock take for the same bin are excluded,
    so stale rows from a previous count cannot drive conflict hints, block
    resolution, or be swept into a paired resolution. This is the single source
    of truth for "is this code a live discrepancy somewhere".
    """
    superseded = StockTake.objects.filter(
        storage_bin=OuterRef("stock_take__storage_bin"),
        stock_take_datetime__gt=OuterRef("stock_take__stock_take_datetime"),
    )
    return (
        StockTakeItem.objects.filter(
            code__in=list(codes),
            status__in=list(statuses),
            stock_transaction__isnull=True,
            acknowledged_datetime__isnull=True,
        )
        .annotate(_superseded=Exists(superseded))
        .filter(_superseded=False)
    )


def _first_other_bin(
    scans: dict[str, list[StockTakeItem]], code: str, status: str, own_bin_id: int
) -> StockTakeItem | None:
    """Most recent unresolved item for ``code`` with ``status`` in another bin."""
    return next(
        (
            s
            for s in scans.get(code, [])
            if s.status == status and s.stock_take.storage_bin_id != own_bin_id
        ),
        None,
    )


def annotate_conflicts(items: list[StockTakeItem]) -> None:
    """Tag each item with a cross-bin ``conflict``/``conflict_level`` hint.

    * A *missing* item whose code is also an **unresolved unexpected** scan in
      another bin is flagged as a warning ("may be misfiled, not lost").
    * Otherwise, if the code is currently registered in a different bin, that is
      shown as info ("now registered in / registered in bin X").

    The presence of any conflict means the item is accounted for elsewhere, so a
    missing item is offered *acknowledge* rather than *lost*.
    """
    for item in items:
        item.conflict = ""
        item.conflict_level = ""
    if not items:
        return

    codes = {i.code for i in items}
    registration = {
        sbi.code: sbi.storage_bin
        for sbi in StorageBinItem.objects.filter(code__in=codes).select_related(
            "storage_bin"
        )
    }
    # Live discrepancies for these codes (latest take per bin), most recent first.
    scans: dict[str, list[StockTakeItem]] = {}
    for sti in (
        open_discrepancies(codes, [MISSING, UNEXPECTED])
        .select_related("stock_take__storage_bin")
        .order_by("-stock_take__stock_take_datetime")
    ):
        scans.setdefault(sti.code, []).append(sti)

    for item in items:
        own_bin_id = item.stock_take.storage_bin_id
        reg = registration.get(item.code)
        if item.status == MISSING:
            other = _first_other_bin(scans, item.code, UNEXPECTED, own_bin_id)
            if other:
                item.conflict = (
                    f"Also scanned as unexpected in bin "
                    f"{other.stock_take.storage_bin.bin_identifier} "
                    f"({to_local(other.stock_take.stock_take_datetime).date()}) — "
                    f"may be misfiled, not lost."
                )
                item.conflict_level = "warning"
            elif reg and reg.pk != own_bin_id:
                item.conflict = f"Now registered in bin {reg.bin_identifier}."
                item.conflict_level = "info"
        elif item.status == UNEXPECTED and reg and reg.pk != own_bin_id:
            item.conflict = f"Registered in bin {reg.bin_identifier}."
            item.conflict_level = "info"
