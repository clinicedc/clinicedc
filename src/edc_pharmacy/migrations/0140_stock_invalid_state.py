from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("edc_pharmacy", "0139_historicalstocktransaction_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="stock",
            name="invalid_state",
            field=models.BooleanField(
                default=False,
                help_text="Pre-refactor data corruption; excluded from ledger bootstrap/checks.",
            ),
        ),
        migrations.AddField(
            model_name="historicalstock",
            name="invalid_state",
            field=models.BooleanField(
                default=False,
                help_text="Pre-refactor data corruption; excluded from ledger bootstrap/checks.",
            ),
        ),
    ]
