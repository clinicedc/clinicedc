import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("edc_action_item", "0010_auto_20181009_0445"),
        ("edc_locator", "0011_auto_20181007_0053"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalsubjectlocator",
            name="parent_action_item",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="edc_action_item.ActionItem",
            ),
        ),
        migrations.AddField(
            model_name="historicalsubjectlocator",
            name="related_action_item",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="edc_action_item.ActionItem",
            ),
        ),
        migrations.AddField(
            model_name="subjectlocator",
            name="parent_action_item",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="edc_action_item.ActionItem",
            ),
        ),
        migrations.AddField(
            model_name="subjectlocator",
            name="related_action_item",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="edc_action_item.ActionItem",
            ),
        ),
    ]
