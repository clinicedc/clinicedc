from __future__ import annotations

from ..database import Database
from ..df_handlers import DfHandler
from ..utils import get_export_folder, get_table_names
from .csv_exporter import CsvExporter


class TablesExporterError(Exception):
    pass


class InvalidTableName(Exception):
    pass


class TablesExporter:

    """Export to file all tables for an app_label.

    Does not decrypt values stored in django_crypto_fields
    encrypted field classes.

    Usage:
        exporter = TablesExporter(app_label='td')
        exporter.to_csv()
        exporter = TablesExporter(app_label='edc')
        exporter.to_csv()

    """

    app_label = None
    csv_exporter_cls = CsvExporter
    db_cls = Database
    delimiter = "|"
    df_handler_cls = DfHandler
    exclude_history_tables = False
    excluded_app_labels = ["django_collect_offline"]

    def __init__(
        self,
        app_label: str | None = None,
        with_columns: list[str] | None = None,
        without_columns: list[str] | None = None,
        exclude_history_tables: bool | None = None,
        exclude_table_hints: bool | None = None,
        export_folder: str | None = None,
        **kwargs,
    ):
        self.app_label = app_label or self.app_label
        if not self.app_label:
            raise TablesExporterError(f"Missing app_label. Got None. See {repr(self)}")
        self.export_folder = export_folder or get_export_folder()
        self.with_columns = with_columns or []
        self.without_columns = without_columns or []
        exclude_table_hints = exclude_table_hints or []
        self.exclude_history_tables = (
            self.exclude_history_tables
            if exclude_history_tables is None
            else exclude_history_tables
        )
        self.exported_paths = {}
        self.db = self.db_cls()
        self.table_names = self.get_table_names()
        if not self.table_names:
            raise TablesExporterError(
                f"No tables found for app_label. Got {self.app_label}. See {repr(self)}"
            )
        for hint in exclude_table_hints:
            for table_name in self.get_table_names():
                if hint in table_name:
                    self.table_names.pop(self.table_names.index(table_name))
        if self.exclude_history_tables:
            self.table_names = [
                tbl
                for tbl in self.table_names
                if "historical" not in tbl and not tbl.endswith("_audit")
            ]

    def __repr__(self):
        return f"{self.__class__.__name__}(app_label='{self.app_label}')"

    def to_csv(
        self, table_names: list[str] | None = None, export_folder: str | None = None, **kwargs
    ):
        """Exports all tables to CSV as raw tables.

        See also `ModelToDataframe` for less generic export options.
        """
        self.exported_paths = {}
        export_folder = export_folder or self.export_folder
        if table_names:
            for table_name in table_names:
                if table_name not in self.table_names:
                    raise InvalidTableName(f"{table_name} is not a valid for {self}")
            self.table_names = table_names
        for table_name in self.table_names:
            df = self.to_df(table_name=table_name, **kwargs)
            exporter = self.csv_exporter_cls(
                table_name=table_name, export_folder=export_folder, **kwargs
            )
            exported = exporter.to_csv(dataframe=df, export_folder=export_folder)
            if exported.path:
                self.exported_paths.update({table_name: exported.path})

    def get_table_names(self) -> list[str]:
        """Returns a list of table names for this app_label."""
        return get_table_names(
            app_label=self.app_label,
            with_columns=self.with_columns,
            without_columns=self.without_columns,
            db_cls=self.db_cls,
        )

    def to_df(self, table_name: str = None, **kwargs):
        """Returns a dataframe after passing the raw df
        through the df_handler class.
        """
        df = self.get_raw_df(table_name)
        if self.df_handler_cls:
            df_handler = self.df_handler_cls(
                dataframe=df, db=self.db, table_name=table_name, **kwargs
            )
            df = df_handler.dataframe
        return df

    def get_raw_df(self, table_name: str = None):
        """Returns a df for the given table_name
        from an SQL statement, that is; raw).
        """
        return self.db.select_table(table_name=table_name)
