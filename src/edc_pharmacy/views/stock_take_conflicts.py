"""Cross-bin conflict annotation for stock take discrepancies.

Shared by the discrepancy report and the results page so both render the same
hints and the same missing-item resolution choice (lost vs acknowledge).
"""

from __future__ import annotations

from edc_utils.date import to_local

from ..models import MISSING, UNEXPECTED, StockTakeItem, StorageBinItem


def _first_other_bin(scans, code, status, own_bin_id):
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
    # Unresolved discrepancies for these codes, most recent first.
    scans: dict[str, list[StockTakeItem]] = {}
    for sti in (
        StockTakeItem.objects.filter(code__in=codes, stock_transaction__isnull=True)
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
