"""Verify the Stock ↔ Allocation invariant.

Two invariants are enforced by the sticky-pointer policy
(see DESIGN_transaction_log.md §5.6):

1. **At most one active Allocation per Stock.** Many Allocation rows may
   exist for a single Stock, but only one may have
   ``ended_datetime IS NULL`` at any time. This is also enforced at the
   DB level by the partial UniqueConstraint
   ``one_active_allocation_per_stock``; running this command pre-migration
   confirms the constraint can be applied to existing data.

2. **Cache agreement.** When ``Stock.allocation_id`` is set, the pointed-to
   Allocation row must satisfy ``Allocation.stock_id == Stock.id``. The
   sticky pointer is allowed to reference an *ended* Allocation (that is
   the whole point of the policy), but it must never reference an
   Allocation that belongs to a different Stock.

3. **Active-cache agreement.** If the most recent Allocation for a Stock
   is active (ended_datetime IS NULL), then ``Stock.allocation_id`` must
   equal that Allocation's id. (A divergence here means the cache fell
   behind the canonical row.)

Exit codes
----------
0 — invariants hold
1 — at least one violation found
"""

from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db.models import Count, F, Q

from ...models import Allocation, Stock


class Command(BaseCommand):
    help = "Verify Stock ↔ Allocation cache invariants (read-only)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Cap the number of violations printed per category (default: all).",
        )
        parser.add_argument(
            "--quiet",
            action="store_true",
            help="Suppress per-violation detail; print only summary counts.",
        )

    def handle(self, *args, **options):  # noqa: ARG002
        limit: int | None = options["limit"]
        quiet: bool = options["quiet"]
        violations = 0

        violations += self._check_duplicate_active_allocations(limit, quiet)
        violations += self._check_cache_points_to_correct_stock(limit, quiet)
        violations += self._check_cache_matches_active_allocation(limit, quiet)

        self.stdout.write("")
        if violations:
            self.stdout.write(
                self.style.ERROR(f"FAIL — {violations} invariant violation(s) found.")
            )
            raise SystemExit(1)
        self.stdout.write(self.style.SUCCESS("OK — all invariants hold."))

    # ------------------------------------------------------------------
    # 1. At most one active Allocation per Stock.
    # ------------------------------------------------------------------
    def _check_duplicate_active_allocations(self, limit, quiet) -> int:
        self.stdout.write(self.style.MIGRATE_HEADING("[1/3] Active-allocation uniqueness"))
        dups = (
            Allocation.objects.filter(ended_datetime__isnull=True)
            .values("stock_id")
            .annotate(n=Count("id"))
            .filter(n__gt=1)
            .order_by("-n")
        )
        count = dups.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS("  OK — no Stock has >1 active Allocation."))
            return 0
        self.stdout.write(
            self.style.ERROR(
                f"  FAIL — {count} stock(s) have multiple active Allocation rows."
            )
        )
        if not quiet:
            for row in dups[: (limit or count)]:
                self.stdout.write(
                    f"    stock_id={row['stock_id']}  active_allocations={row['n']}"
                )
        return count

    # ------------------------------------------------------------------
    # 2. Cache points to an Allocation that belongs to this Stock.
    # ------------------------------------------------------------------
    def _check_cache_points_to_correct_stock(self, limit, quiet) -> int:
        self.stdout.write(
            self.style.MIGRATE_HEADING("[2/3] Stock.allocation row-ownership consistency")
        )
        # Stock.allocation set, but the pointed-to Allocation.stock disagrees.
        bad = Stock.objects.filter(allocation__isnull=False).exclude(
            allocation__stock_id=F("id")
        )
        count = bad.count()
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    "  OK — every Stock.allocation points to an Allocation "
                    "owned by that same Stock."
                )
            )
            return 0
        self.stdout.write(
            self.style.ERROR(
                f"  FAIL — {count} stock(s) cache an Allocation belonging to a different Stock."
            )
        )
        if not quiet:
            for stock in bad.values("id", "code", "allocation_id")[: (limit or count)]:
                self.stdout.write(
                    f"    stock_id={stock['id']} code={stock['code']} "
                    f"allocation_id={stock['allocation_id']}"
                )
        return count

    # ------------------------------------------------------------------
    # 3. If a Stock has an active Allocation, the cache must point to it.
    # ------------------------------------------------------------------
    def _check_cache_matches_active_allocation(self, limit, quiet) -> int:
        self.stdout.write(
            self.style.MIGRATE_HEADING("[3/3] Stock.allocation == active Allocation (if any)")
        )
        # For every Stock that has at least one active Allocation, the
        # cache must point at it. Equivalent SQL: WHERE EXISTS active
        # AND (allocation_id IS NULL OR allocation.ended_datetime IS NOT NULL).
        active_alloc_stock_ids = set(
            Allocation.objects.filter(ended_datetime__isnull=True).values_list(
                "stock_id", flat=True
            )
        )
        if not active_alloc_stock_ids:
            self.stdout.write(self.style.SUCCESS("  OK — no active allocations to check."))
            return 0

        bad = Stock.objects.filter(id__in=active_alloc_stock_ids).filter(
            Q(allocation__isnull=True) | Q(allocation__ended_datetime__isnull=False)
        )
        count = bad.count()
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    "  OK — every Stock with an active Allocation caches it correctly."
                )
            )
            return 0
        self.stdout.write(
            self.style.ERROR(
                f"  FAIL — {count} stock(s) have an active Allocation but the cache disagrees."
            )
        )
        if not quiet:
            for stock in bad.values("id", "code", "allocation_id")[: (limit or count)]:
                self.stdout.write(
                    f"    stock_id={stock['id']} code={stock['code']} "
                    f"cached_allocation_id={stock['allocation_id']}"
                )
        return count
