import pandas as pd

from ..constants import SYSTEM_COLUMNS
from ..df_handlers import NonCrfDfHandler
from .csv_crf_tables_exporter import CsvCrfTablesExporter


class CsvCrfInlineTablesExporter(CsvCrfTablesExporter):

    """A class to export non-CRF tables for this app_label."""

    visit_column = None
    df_inline_handler_cls = NonCrfDfHandler
    exclude_inline_tables = None

    def __init__(self, exclude_inline_tables=None, **kwargs):
        self.exclude_inline_tables = exclude_inline_tables or self.exclude_inline_tables or []
        super().__init__(**kwargs)

    def to_csv(self, export_folder=None, **kwargs):
        """Exports all tables to CSV."""
        self.exported_paths = {}
        export_folder = export_folder or self.export_folder
        for table_name in self.table_names:
            df_table = self.to_df(table_name=table_name, exclude_system_columns=True, **kwargs)
            for row in self.get_inline_table_names(table_name).itertuples():
                if row.table_name not in self.exclude_inline_tables:
                    df_inline = self.to_inline_df(table_name=row.table_name, **kwargs)
                    df = self.merge_with_inline(
                        df_table,
                        df_inline,
                        left_on=row.referenced_column_name,
                        right_on=row.column_name,
                    )
                    df = self.get_prepped_inline_df(table_name=row.table_name, df=df)
                    label = row.column_name.replace("_id", "").replace("_", "")
                    csv_exporter = self.csv_exporter_cls(
                        data_label=f"{row.table_name}_{label}_merged",
                        export_folder=export_folder,
                        **kwargs,
                    )
                    exported = csv_exporter.to_csv(dataframe=df)
                    if exported.path:
                        self.exported_paths.update({table_name: exported.path})

    def get_inline_table_names(self, table_name=None):
        return self.db.show_inline_tables(referenced_table_name=table_name)

    def merge_with_inline(self, df_table=None, df_inline=None, left_on=None, right_on=None):
        """Merge main table and its inline."""
        df_table = df_table[[col for col in df_table.columns if col not in SYSTEM_COLUMNS]]
        df = pd.merge(
            df_table,
            df_inline,
            how="left",
            left_on=left_on,
            right_on=right_on,
            suffixes=["_master", ""],
        )
        return df

    def to_inline_df(self, table_name=None, **kwargs):
        """Returns a "prepped" dataframe for this inline table_name."""
        df = self.get_raw_df(table_name)
        return self.get_prepped_inline_df(table_name, df, **kwargs)

    def get_prepped_inline_df(self, table_name=None, df=None, **kwargs):
        """Returns a dataframe after passing the given inline df
        through the inline df_handler class.
        """
        if self.df_handler_cls:
            df_handler = self.df_inline_handler_cls(
                dataframe=df, db=self.db, table_name=table_name, **kwargs
            )
            df = df_handler.dataframe
        return df
