# Step 3 of 4: Tighten.
#
# Now that the data migration has run:
# - Make Allocation.stock non-null.
# - Add indexes on Allocation for fast active-allocation queries.
#
# Note on partial unique (UNIQUE stock_id WHERE ended_datetime IS NULL):
# MySQL does not support partial unique indexes, so the uniqueness of
# "at most one active allocation per stock" is enforced at the application
# layer in apply_transaction (the TXN_ALLOCATED precondition checks
# current_allocation__isnull=True before creating a new Allocation).

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("edc_pharmacy", "0143_allocation_refactor_step2_data"),
    ]

    operations = [
        # Allocation.stock is now always populated — make it non-null.
        migrations.AlterField(
            model_name="allocation",
            name="stock",
            field=models.ForeignKey(
                help_text="Stock item allocated to this subject.",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="allocations",
                to="edc_pharmacy.stock",
            ),
        ),
        # Index: fast lookup of all allocations for a stock ordered by time.
        migrations.AddIndex(
            model_name="allocation",
            index=models.Index(
                fields=["stock", "-started_datetime"],
                name="edc_pharm_stock_started_idx",
            ),
        ),
        # Index: fast "active only" filter (WHERE ended_datetime IS NULL).
        migrations.AddIndex(
            model_name="allocation",
            index=models.Index(
                fields=["ended_datetime"],
                name="edc_pharm_alloc_ended_idx",
            ),
        ),
    ]
