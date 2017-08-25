import pandas as pd

from django.core.management.color import color_style

from ..db import Engine, Credentials
from .dialect import Dialect

style = color_style()


class DbConnectionError(Exception):
    pass


class MysqlDb:

    engine_cls = Engine
    credentials_cls = Credentials
    dialect_cls = Dialect
    engine_name = 'mysql'

    def __init__(self, credentials=None, **kwargs):
        self.credentials = credentials or self.credentials_cls(**kwargs)
        self.database = credentials.dbname
        self.dialect = self.dialect_cls(dbname=credentials.dbname)
        self.engine = self.engine_cls(
            name=self.engine_name, credentials=credentials).engine
        self.verify_dbname()
        self._tables = pd.DataFrame()

    def verify_dbname(self):
        df = self.show_databases()
        databases = list(df.database)
        if self.credentials.dbname not in databases:
            raise DbConnectionError(
                f'Unknown database {self.credentials.dbname}. '
                f'Available databases are {", ".join(databases)}')

    def read_sql(self, sql=None):
        """Returns a dataframe. A simple wrapper for pd.read_sql().
        """
        with self.engine.connect() as conn, conn.begin():
            df = pd.read_sql(sql, conn)
        return df

    def show_databases(self):
        """Returns a dataframe of database names in the schema.
        """
        with self.engine.connect() as conn, conn.begin():
            df = pd.read_sql(
                self.dialect.show_databases(), conn)
        return df

    def select_table(self, table_name=None):
        """Returns a dataframe of a table.
        """
        with self.engine.connect() as conn, conn.begin():
            df = pd.read_sql(
                self.dialect.select_table(table_name), conn)
        return df

    def show_tables(self, app_label=None):
        """Returns a dataframe of table names in the schema.
        """
        with self.engine.connect() as conn, conn.begin():
            df = pd.read_sql(
                self.dialect.show_tables(app_label), conn)
        return df

    def show_tables_with_columns(self, app_label=None, column_names=None):
        """Returns a dataframe of table names in the schema.
        """
        with self.engine.connect() as conn, conn.begin():
            df = pd.read_sql(
                self.dialect.show_tables_with_columns(app_label, column_names), conn)
        return df

    def to_df(self, table_name=None, rename_columns=None, force_lower_columns=None):
        """Returns as a dataframe.
        """
        force_lower_columns = True if force_lower_columns is None else force_lower_columns
        with self.engine.connect() as conn, conn.begin():
            df = pd.read_sql_table(table_name, conn)
        if rename_columns:
            df.rename(columns=rename_columns, inplace=True)
        if force_lower_columns:
            columns = {col: col.lower() for col in list(df.columns)}
            df.rename(columns=columns, inplace=True)
        return df
