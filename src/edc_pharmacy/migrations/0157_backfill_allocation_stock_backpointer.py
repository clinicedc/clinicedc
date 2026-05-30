"""Backfill Allocation.stock back-pointer for legacy rows.

Stocks created via the pre-2026-05-07 ``allocate_stock`` util set
``Stock.allocation`` but never set ``Allocation.stock`` (the reverse
back-pointer). The forward FK is the authoritative side, so historical
data is consistent — but readers that traverse ``allocation.stock`` see
``None`` for any Allocation written by that code path.

This migration walks every Stock whose ``allocation`` is set and whose
linked Allocation has ``stock_id IS NULL``, then copies the back-pointer
in via a bulk-friendly ``UPDATE``.

Forward is idempotent: running it twice is a no-op on the second pass.
Reverse is a no-op — re-NULLing rows would be unsafe once new code
(post-2026-05-07) has correctly populated them.
"""

from django.db import migrations
from tqdm import tqdm


def backfill_allocation_stock(apps, schema_editor):
    Stock = apps.get_model("edc_pharmacy", "stock")
    Allocation = apps.get_model("edc_pharmacy", "allocation")

    pairs = list(
        Stock.objects.filter(
            allocation__isnull=False, allocation__stock__isnull=True
        ).values_list("allocation_id", "id")
    )
    if not pairs:
        return

    for allocation_id, stock_id in tqdm(pairs, total=len(pairs)):
        Allocation.objects.filter(pk=allocation_id, stock__isnull=True).update(
            stock_id=stock_id
        )


def reverse_noop(apps, schema_editor):
    # Reversing this backfill would re-NULL rows that may be correctly
    # set by post-migration code. Safer to be a no-op.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("edc_pharmacy", "0156_alter_historicalorder_status_and_more"),
    ]

    operations = [migrations.RunPython(backfill_allocation_stock, reverse_noop)]
