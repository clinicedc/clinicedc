"""Stock take discrepancy report.

Shows only bins whose most recent stock take has missing or unexpected items,
grouped by location.

Each discrepancy is annotated with a cross-bin *conflict* hint so the user does
not, for example, mark an item Lost when it is actually sitting in another bin
as an unexpected scan.
"""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin
from edc_utils.date import to_local

from ..models import (
    MISSING,
    UNEXPECTED,
    StockTake,
    StockTakeItem,
    StorageBin,
    StorageBinItem,
)


@method_decorator(login_required, name="dispatch")
class StockTakeDiscrepancyReportView(
    EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView
):
    template_name = "edc_pharmacy/stock/stock_take_discrepancy_report.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_context_data(self, **kwargs):
        bins = (
            StorageBin.objects.filter(in_use=True)
            .select_related("container", "location")
            .order_by("location__display_name", "bin_identifier")
        )

        # One flat, bin-ordered list of discrepancies (missing then unexpected
        # within each bin) for a single grouped DataTable.
        items: list[StockTakeItem] = []
        for b in bins:
            last = (
                StockTake.objects.filter(storage_bin=b)
                .order_by("-stock_take_datetime")
                .first()
            )
            if not last or (last.missing_count == 0 and last.unexpected_count == 0):
                continue
            # Reuse the already-loaded bin (with container/location) for URLs.
            last.storage_bin = b

            bin_items = list(
                last.items.filter(status__in=(MISSING, UNEXPECTED))
                .select_related("stock__product")
                .order_by("status", "code")
            )
            # Populate the stock_take FK cache so neither conflict annotation nor
            # the template re-queries it per item.
            for item in bin_items:
                item.stock_take = last
            items.extend(bin_items)

        self._annotate_conflicts(items)
        return super().get_context_data(items=items, **kwargs)

    def _annotate_conflicts(self, items: list[StockTakeItem]) -> None:
        """Tag each item with a cross-bin ``conflict``/``conflict_level`` hint.

        * A *missing* item whose code is also an **unresolved unexpected** scan in
          another bin is flagged as a warning ("may be misfiled, not lost").
        * Otherwise, if the code is currently registered in a different bin, that
          is shown as info ("now registered in / registered in bin X").
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
                other = self._first_other_bin(scans, item.code, UNEXPECTED, own_bin_id)
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

    @staticmethod
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
