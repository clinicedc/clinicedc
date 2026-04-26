# Step 4 of 4: Drop the legacy Stock.allocation OneToOneField.
#
# All Python call sites now use stock.current_allocation instead.
# The database column edc_pharmacy_stock.allocation_id is no longer needed.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("edc_pharmacy", "0144_allocation_refactor_step3_tighten"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="stock",
            name="allocation",
        ),
        migrations.RemoveField(
            model_name="historicalstock",
            name="allocation",
        ),
    ]
