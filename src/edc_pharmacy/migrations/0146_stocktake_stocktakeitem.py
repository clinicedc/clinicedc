import django.db.models.deletion
import django.utils.timezone
import django_audit_fields.fields.uuid_auto_field
import edc_model.models.fields.date_estimated
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("edc_pharmacy", "0145_allocation_refactor_step4_drop"),
        ("sites", "0002_alter_domain_unique"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="StockTake",
            fields=[
                (
                    "id",
                    django_audit_fields.fields.uuid_auto_field.UUIDAutoField(
                        blank=True,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ("modified", models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ("user_created", models.CharField(blank=True, db_index=True, max_length=50)),
                ("user_modified", models.CharField(blank=True, db_index=True, max_length=50)),
                (
                    "hostname_created",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="System field. (modified on create only)",
                        max_length=60,
                    ),
                ),
                (
                    "hostname_modified",
                    models.CharField(
                        blank=True,
                        default=django.utils.timezone.now,
                        max_length=50,
                    ),
                ),
                ("revision", models.CharField(blank=True, max_length=75, null=True)),
                ("locale", models.CharField(blank=True, max_length=10, null=True)),
                ("device_created", models.CharField(blank=True, max_length=10)),
                ("device_modified", models.CharField(blank=True, max_length=10)),
                (
                    "stock_take_identifier",
                    models.CharField(
                        blank=True,
                        editable=False,
                        max_length=36,
                        null=True,
                        unique=True,
                    ),
                ),
                (
                    "stock_take_datetime",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("in_progress", "In progress"), ("completed", "Completed")],
                        default="in_progress",
                        max_length=25,
                    ),
                ),
                (
                    "expected_count",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Number of items registered in the bin at the time of the stock take.",
                    ),
                ),
                (
                    "scanned_count",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Number of codes scanned during the stock take.",
                    ),
                ),
                ("matched_count", models.PositiveIntegerField(default=0)),
                ("missing_count", models.PositiveIntegerField(default=0)),
                ("unexpected_count", models.PositiveIntegerField(default=0)),
                ("note", models.TextField(blank=True, default="")),
                (
                    "performed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "site",
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="sites.site",
                    ),
                ),
                (
                    "storage_bin",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="stock_takes",
                        to="edc_pharmacy.storagebin",
                    ),
                ),
            ],
            options={
                "verbose_name": "Stock take",
                "verbose_name_plural": "Stock takes",
                "ordering": ["-stock_take_datetime"],
            },
        ),
        migrations.CreateModel(
            name="HistoricalStockTake",
            fields=[
                (
                    "id",
                    django_audit_fields.fields.uuid_auto_field.UUIDAutoField(
                        blank=True,
                        db_index=True,
                        editable=False,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ("modified", models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ("user_created", models.CharField(blank=True, db_index=True, max_length=50)),
                ("user_modified", models.CharField(blank=True, db_index=True, max_length=50)),
                (
                    "hostname_created",
                    models.CharField(blank=True, default="", max_length=60),
                ),
                (
                    "hostname_modified",
                    models.CharField(blank=True, default=django.utils.timezone.now, max_length=50),
                ),
                ("revision", models.CharField(blank=True, max_length=75, null=True)),
                ("locale", models.CharField(blank=True, max_length=10, null=True)),
                ("device_created", models.CharField(blank=True, max_length=10)),
                ("device_modified", models.CharField(blank=True, max_length=10)),
                (
                    "stock_take_identifier",
                    models.CharField(blank=True, editable=False, max_length=36, null=True),
                ),
                (
                    "stock_take_datetime",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("in_progress", "In progress"), ("completed", "Completed")],
                        default="in_progress",
                        max_length=25,
                    ),
                ),
                ("expected_count", models.PositiveIntegerField(default=0)),
                ("scanned_count", models.PositiveIntegerField(default=0)),
                ("matched_count", models.PositiveIntegerField(default=0)),
                ("missing_count", models.PositiveIntegerField(default=0)),
                ("unexpected_count", models.PositiveIntegerField(default=0)),
                ("note", models.TextField(blank=True, default="")),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "performed_by",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "site",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="sites.site",
                    ),
                ),
                (
                    "storage_bin",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="edc_pharmacy.storagebin",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical Stock take",
                "verbose_name_plural": "historical Stock takes",
                "ordering": ["-history_date", "-history_id"],
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="StockTakeItem",
            fields=[
                (
                    "id",
                    django_audit_fields.fields.uuid_auto_field.UUIDAutoField(
                        blank=True,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ("modified", models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ("user_created", models.CharField(blank=True, db_index=True, max_length=50)),
                ("user_modified", models.CharField(blank=True, db_index=True, max_length=50)),
                (
                    "hostname_created",
                    models.CharField(blank=True, default="", max_length=60),
                ),
                (
                    "hostname_modified",
                    models.CharField(blank=True, default=django.utils.timezone.now, max_length=50),
                ),
                ("revision", models.CharField(blank=True, max_length=75, null=True)),
                ("locale", models.CharField(blank=True, max_length=10, null=True)),
                ("device_created", models.CharField(blank=True, max_length=10)),
                ("device_modified", models.CharField(blank=True, max_length=10)),
                ("code", models.CharField(max_length=15, verbose_name="Stock code")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("matched", "Matched"),
                            ("missing", "Missing"),
                            ("unexpected", "Unexpected"),
                        ],
                        max_length=15,
                    ),
                ),
                (
                    "stock",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="edc_pharmacy.stock",
                    ),
                ),
                (
                    "stock_take",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="items",
                        to="edc_pharmacy.stocktake",
                    ),
                ),
            ],
            options={
                "verbose_name": "Stock take item",
                "verbose_name_plural": "Stock take items",
                "ordering": ["status", "code"],
            },
        ),
        migrations.CreateModel(
            name="HistoricalStockTakeItem",
            fields=[
                (
                    "id",
                    django_audit_fields.fields.uuid_auto_field.UUIDAutoField(
                        blank=True,
                        db_index=True,
                        editable=False,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ("modified", models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ("user_created", models.CharField(blank=True, db_index=True, max_length=50)),
                ("user_modified", models.CharField(blank=True, db_index=True, max_length=50)),
                (
                    "hostname_created",
                    models.CharField(blank=True, default="", max_length=60),
                ),
                (
                    "hostname_modified",
                    models.CharField(blank=True, default=django.utils.timezone.now, max_length=50),
                ),
                ("revision", models.CharField(blank=True, max_length=75, null=True)),
                ("locale", models.CharField(blank=True, max_length=10, null=True)),
                ("device_created", models.CharField(blank=True, max_length=10)),
                ("device_modified", models.CharField(blank=True, max_length=10)),
                ("code", models.CharField(max_length=15, verbose_name="Stock code")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("matched", "Matched"),
                            ("missing", "Missing"),
                            ("unexpected", "Unexpected"),
                        ],
                        max_length=15,
                    ),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "stock",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="edc_pharmacy.stock",
                    ),
                ),
                (
                    "stock_take",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="edc_pharmacy.stocktake",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical Stock take item",
                "verbose_name_plural": "historical Stock take items",
                "ordering": ["-history_date", "-history_id"],
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
