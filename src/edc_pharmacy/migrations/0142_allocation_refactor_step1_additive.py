# Step 1 of 4: Additive.
#
# - Stock.allocation OneToOneField gets related_name="allocation_legacy" to free
#   up the "stock" reverse-accessor name on Allocation.
# - Add Allocation.stock FK (null=True for now).
# - Add Allocation.started_datetime, ended_datetime, ended_reason.
# - Add Stock.current_allocation FK (null=True for now).
#
# No data movement. Safe to deploy before the data migration.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("edc_pharmacy", "0141_historicalreturnrequest_returnitem_and_more"),
    ]

    operations = [
        # Free up the "stock" reverse-accessor name so Allocation.stock FK can use it.
        migrations.AlterField(
            model_name="stock",
            name="allocation",
            field=models.OneToOneField(
                blank=True,
                help_text="Legacy OneToOne — replaced by current_allocation FK. "
                          "Dropped in migration 0145.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="allocation_legacy",
                to="edc_pharmacy.allocation",
            ),
        ),
        migrations.AlterField(
            model_name="historicalstock",
            name="allocation",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="edc_pharmacy.allocation",
            ),
        ),
        # Add Allocation.stock FK (null=True until data migration populates it).
        migrations.AddField(
            model_name="allocation",
            name="stock",
            field=models.ForeignKey(
                blank=True,
                help_text="Stock item allocated to this subject.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="allocations",
                to="edc_pharmacy.stock",
            ),
        ),
        migrations.AddField(
            model_name="historicalallocation",
            name="stock",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="edc_pharmacy.stock",
            ),
        ),
        # Allocation lifecycle timestamps.
        migrations.AddField(
            model_name="allocation",
            name="started_datetime",
            field=models.DateTimeField(
                blank=True,
                null=True,
                help_text="When the allocation became active (defaults to allocation_datetime).",
            ),
        ),
        migrations.AddField(
            model_name="historicalallocation",
            name="started_datetime",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="allocation",
            name="ended_datetime",
            field=models.DateTimeField(
                blank=True,
                db_index=True,
                null=True,
                help_text="When the allocation ended (NULL = still active).",
            ),
        ),
        migrations.AddField(
            model_name="historicalallocation",
            name="ended_datetime",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="allocation",
            name="ended_reason",
            field=models.CharField(
                blank=True,
                default="",
                max_length=50,
                help_text="Why the allocation ended (dispensed, returned, reallocated, …).",
            ),
        ),
        migrations.AddField(
            model_name="historicalallocation",
            name="ended_reason",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        # Add Stock.current_allocation FK (null=True until data migration).
        migrations.AddField(
            model_name="stock",
            name="current_allocation",
            field=models.ForeignKey(
                blank=True,
                help_text="Active allocation for this stock item (NULL if unallocated or dispensed).",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="edc_pharmacy.allocation",
            ),
        ),
        migrations.AddField(
            model_name="historicalstock",
            name="current_allocation",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="edc_pharmacy.allocation",
            ),
        ),
    ]
