# Step 2 of 4: Data migration.
#
# For every Allocation:
#   - Set allocation.stock_id from the old Stock.allocation OneToOne reverse,
#     falling back to Stock.objects.filter(code=allocation.code) for stocks
#     where the FK was already nulled (dispensed stocks fixed by
#     fix_historical_stock_state).
#   - Set started_datetime = allocation_datetime (best available proxy).
#   - If stock.dispensed: set ended_datetime = stock.stock_datetime,
#     ended_reason = "dispensed".
#
# For every non-dispensed Stock that still has allocation_id set:
#   - Set stock.current_allocation_id = stock.allocation_id.

from django.db import migrations


def populate_forward(apps, schema_editor):
    Allocation = apps.get_model("edc_pharmacy", "Allocation")
    Stock = apps.get_model("edc_pharmacy", "Stock")

    # Build a lookup: allocation_pk → stock via the old OneToOne reverse.
    # stock.allocation_id is the old FK column (still present at this migration step).
    stock_by_alloc = {
        s.allocation_id: s
        for s in Stock.objects.filter(allocation__isnull=False).only(
            "pk", "allocation_id", "code", "dispensed", "stock_datetime"
        )
    }

    alloc_updates = []
    stock_current_updates = []

    for alloc in Allocation.objects.only(
        "pk", "allocation_datetime", "code", "stock_id", "started_datetime",
        "ended_datetime", "ended_reason",
    ):
        stock = stock_by_alloc.get(alloc.pk)

        if stock is None:
            # Dispensed stock whose allocation FK was already nulled — find via code.
            stock = Stock.objects.filter(code=alloc.code).only(
                "pk", "code", "dispensed", "stock_datetime"
            ).first()

        if stock is None:
            continue

        alloc.stock_id = stock.pk
        alloc.started_datetime = alloc.allocation_datetime
        if stock.dispensed:
            alloc.ended_datetime = alloc.ended_datetime or stock.stock_datetime
            alloc.ended_reason = alloc.ended_reason or "dispensed"

        alloc_updates.append(alloc)

        if not stock.dispensed:
            stock.current_allocation_id = alloc.pk
            stock_current_updates.append(stock)

    if alloc_updates:
        Allocation.objects.bulk_update(
            alloc_updates,
            ["stock", "started_datetime", "ended_datetime", "ended_reason"],
            batch_size=500,
        )
    if stock_current_updates:
        Stock.objects.bulk_update(
            stock_current_updates,
            ["current_allocation"],
            batch_size=500,
        )


def reverse_populate(apps, schema_editor):
    """Reverse: clear the newly populated columns."""
    Allocation = apps.get_model("edc_pharmacy", "Allocation")
    Stock = apps.get_model("edc_pharmacy", "Stock")
    Allocation.objects.all().update(
        stock=None, started_datetime=None, ended_datetime=None, ended_reason=""
    )
    Stock.objects.all().update(current_allocation=None)


class Migration(migrations.Migration):

    dependencies = [
        ("edc_pharmacy", "0142_allocation_refactor_step1_additive"),
    ]

    operations = [
        migrations.RunPython(populate_forward, reverse_code=reverse_populate),
    ]
