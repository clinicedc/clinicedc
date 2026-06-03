"""MySQL-only enforcement of one active Allocation per Stock.

The Meta ``UniqueConstraint(condition=Q(ended_datetime__isnull=True))``
becomes a partial unique index on PostgreSQL / SQLite but is silently
skipped on MySQL — partial indexes don't exist there. This migration
reproduces the invariant on MySQL with the canonical workaround:

  * A STORED generated column ``active_stock_id`` equal to ``stock_id``
    when ``ended_datetime IS NULL`` and ``NULL`` otherwise.
  * A plain unique index on that column.

Why it works: MySQL unique indexes treat ``NULL`` values as distinct, so
ended Allocation rows (active_stock_id = NULL) coexist freely with
others for the same stock; only the active row (active_stock_id =
stock_id) is uniqueness-checked.

No-op on every non-MySQL backend so the partial index that Django emits
from the Meta constraint stays intact there.

Requirements:
  * MySQL >= 5.7.6 for STORED generated columns.
  * InnoDB engine (Django's default).

Reversible. ``unmigrate`` drops the index and the column on MySQL only.
"""

from django.db import migrations

MYSQL_FORWARD_SQL = """
    ALTER TABLE edc_pharmacy_allocation
        ADD COLUMN active_stock_id CHAR(32)
            GENERATED ALWAYS AS (
                CASE WHEN ended_datetime IS NULL THEN stock_id ELSE NULL END
            ) STORED,
        ADD UNIQUE INDEX one_active_allocation_per_stock_mysql (active_stock_id);
"""

MYSQL_REVERSE_SQL = """
    ALTER TABLE edc_pharmacy_allocation
        DROP INDEX one_active_allocation_per_stock_mysql,
        DROP COLUMN active_stock_id;
"""


def forward(apps, schema_editor):  # noqa: ARG001
    if schema_editor.connection.vendor != "mysql":
        return
    schema_editor.execute(MYSQL_FORWARD_SQL)


def reverse(apps, schema_editor):  # noqa: ARG001
    if schema_editor.connection.vendor != "mysql":
        return
    schema_editor.execute(MYSQL_REVERSE_SQL)


class Migration(migrations.Migration):

    dependencies = [
        ("edc_pharmacy", "0157_backfill_allocation_stock_backpointer"),
    ]

    operations = [
        migrations.RunPython(forward, reverse),
    ]
