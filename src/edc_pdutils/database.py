from __future__ import annotations

from typing import TYPE_CHECKING
from urllib import parse
from uuid import UUID

import numpy as np
import pandas as pd
from django.conf import settings
from sqlalchemy import TextClause, create_engine, text

from .dialects import MysqlDialect

if TYPE_CHECKING:
    from sqlalchemy import Engine


class DatabaseNameError(Exception):
    pass


class Database:
    dialect_cls = MysqlDialect
    lowercase_columns = True
    DATABASES_NAME = "default"

    def __init__(self):
        self._database = None
        self._engine: Engine | None = None
        self._tables = pd.DataFrame()
        self.dialect = self.dialect_cls(dbname=self.database)

    @property
    def engine(self) -> Engine:
        if not self._engine:
            db_settings = settings.DATABASES.get("default")
            user = db_settings.get("USER")
            pwd = parse.quote(db_settings.get("PASSWORD"))
            name = db_settings.get("NAME")
            host = db_settings.get("HOST")
            port = db_settings.get("PORT")
            uri = f"mysql://{user}:{pwd}@{host}:{port}/{name}?charset=utf8"
            self._engine = create_engine(uri)
        return self._engine

    @property
    def database(self) -> dict:
        """Returns the database name."""
        return settings.DATABASES[self.DATABASES_NAME]["NAME"]

    def read_sql(
        self, sql: TextClause, params: list | tuple | dict | None = None
    ) -> pd.DataFrame:
        """Returns a dataframe.

        A simple wrapper for pd.read_sql().
        """
        with self.engine.connect() as conn:
            df = pd.read_sql(sql, conn, params=params)
        return df

    def show_databases(self) -> pd.DataFrame:
        """Returns a dataframe of database names in the schema."""
        sql, params = self.dialect.show_databases()
        return self.read_sql(sql, params=params)

    def select_table(
        self,
        table_name: str = None,
        lowercase_columns: list[str] | None = None,
        uuid_columns: list[str] | None = None,
        limit: int | None = None,
    ) -> pd.DataFrame:
        """Returns a dataframe of a table.

        Note: UUID columns are stored as strings (uuid.hex) and need
        to be converted from string to UUID if to match the
        rendering of the same column by a Django model class.
        """
        uuid_columns = uuid_columns or []
        lowercase_columns = lowercase_columns or self.lowercase_columns
        sql, params = self.dialect.select_table(table_name)
        if limit:
            sql = text(f"{sql.text} LIMIT {int(limit)}")
        df = self.read_sql(sql, params=params)
        if lowercase_columns:
            columns = {col: col.lower() for col in list(df.columns)}
            df.rename(columns=columns, inplace=True)
        for col in uuid_columns:
            df[col] = df.apply(lambda row: str(UUID(row[col])) if row[col] else np.nan, axis=1)
        return df

    def show_tables(self, app_label: str = None) -> pd.DataFrame:
        """Returns a dataframe of table names in the schema."""
        sql, params = self.dialect.show_tables(app_label)
        return self.read_sql(sql, params=params)

    def show_tables_with_columns(
        self, app_label: str = None, column_names: list[str] = None
    ) -> pd.DataFrame:
        """Returns a dataframe of table names in the schema
        that have a column in column_names.
        """
        sql, params = self.dialect.show_tables_with_columns(app_label, column_names)
        return self.read_sql(sql, params=params)

    def show_tables_without_columns(
        self, app_label: str = None, column_names: list[str] = None
    ) -> pd.DataFrame:
        """Returns a dataframe of table names in the schema.
        that DO NOT have a column in column_names.
        """
        sql, params = self.dialect.show_tables_without_columns(app_label, column_names)
        return self.read_sql(sql, params=params)

    def show_inline_tables(self, referenced_table_name: str = None):
        sql, params = self.dialect.show_inline_tables(referenced_table_name)
        df = self.read_sql(sql, params=params)
        df = df.rename(
            columns={
                "TABLE_NAME": "table_name",
                "REFERENCED_COLUMN_NAME": "referenced_column_name",
                "REFERENCED_TABLE_NAME": "referenced_table_name",
                "COLUMN_NAME": "column_name",
            }
        )
        return df
