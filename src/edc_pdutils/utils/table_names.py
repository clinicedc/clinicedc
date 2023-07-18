from __future__ import annotations

from typing import Type

from ..database import Database


def get_table_names(
    app_label: str,
    with_columns: list[str] | None = None,
    without_columns: list[str] | None = None,
    db_cls: Type[Database] | None = None,
) -> list[str]:
    """Returns a list of table names for this app_label."""
    db = (db_cls or Database)()

    if with_columns:
        df = db.show_tables_with_columns(app_label, with_columns)
    elif without_columns:
        df = db.show_tables_without_columns(app_label, without_columns)
    else:
        df = db.show_tables(app_label)
    df = df.rename(columns={"TABLE_NAME": "table_name"})
    return list(df.table_name)


def get_model_names(
    app_label: str,
    with_columns: list[str] | None = None,
    without_columns: list[str] | None = None,
    db_cls: Type[Database] | None = None,
    exclude_historical: bool | None = None,
) -> list[str]:
    """Returns a list of table names for this app_label."""
    model_names = []
    for table_name in get_table_names(
        app_label, with_columns=with_columns, without_columns=without_columns, db_cls=db_cls
    ):
        model_name = table_name.split(app_label)[1][1::]
        if exclude_historical and model_name.startswith("historical"):
            continue
        model_names.append(f"{app_label}.{model_name}")
    return model_names
