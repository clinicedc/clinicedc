from __future__ import annotations

from ..database import Database


def get_table_names(
    app_label: str,
    with_columns: list[str] | None = None,
    without_columns: list[str] | None = None,
    db_cls: type[Database] | None = None,
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
    db_cls: type[Database] | None = None,
    exclude_historical: bool | None = None,
    exclude_views: bool | None = None,
) -> list[str]:
    """Returns a list of model names derived from the table name
    for this app_label.

    Will return the wrong model name if the db_table is unmanaged
    and naming does not follow Django convention. `exclude_views`
    is False by default for this reason.

    TODO: why not use django_apps.get_models()? Is it because
          of encrypted fields?
    """
    model_names = []
    exclude_views = True if exclude_views is None else exclude_views
    for table_name in get_table_names(
        app_label,
        with_columns=with_columns,
        without_columns=without_columns,
        db_cls=db_cls,
    ):
        model_name = table_name.split(app_label)[1][1::]
        if (exclude_historical and model_name.startswith("historical")) or (
            exclude_views and model_name.endswith("_view")
        ):
            continue
        model_names.append(f"{app_label}.{model_name}")
    return model_names
