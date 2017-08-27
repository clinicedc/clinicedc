import pandas as pd

from django.conf import settings
from django.db import connection

from .dialects import MysqlDialect


class Database:

    dialect_cls = MysqlDialect
    lowercase_columns = True

    def __init__(self, **kwargs):
        self._tables = pd.DataFrame()
        self.database = settings.DATABASES.get('default').get('NAME')
        self.dialect = self.dialect_cls(dbname=self.database)

    def read_sql(self, sql, params=None):
        """Returns a dataframe. A simple wrapper for pd.read_sql().
        """
        return pd.read_sql(sql, connection, params=params)

    def show_databases(self):
        """Returns a dataframe of database names in the schema.
        """
        sql, params = self.dialect.show_databases()
        return self.read_sql(sql, params=params)

    def select_table(self, table_name=None, lowercase_columns=None):
        """Returns a dataframe of a table.
        """
        lowercase_columns = lowercase_columns or self.lowercase_columns
        sql, params = self.dialect.select_table(table_name)
        df = self.read_sql(sql, params=params)
        if lowercase_columns:
            columns = {col: col.lower() for col in list(df.columns)}
            df.rename(columns=columns, inplace=True)
        return df

    def show_tables(self, app_label=None):
        """Returns a dataframe of table names in the schema.
        """
        sql, params = self.dialect.show_tables(app_label)
        return self.read_sql(sql, params=params)

    def show_tables_with_columns(self, app_label=None, column_names=None):
        """Returns a dataframe of table names in the schema
        that have a column in column_names.
        """
        sql, params = self.dialect.show_tables_with_columns(
            app_label, column_names)
        return self.read_sql(sql, params=params)

    def show_tables_without_columns(self, app_label=None, column_names=None):
        """Returns a dataframe of table names in the schema.
        that DO NOT have a column in column_names.
        """
        sql, params = self.dialect.show_tables_without_columns(
            app_label, column_names)
        return self.read_sql(sql, params=params)

    def show_inline_tables(self, referenced_table_name=None):
        sql, params = self.dialect.show_inline_tables(referenced_table_name)
        return self.read_sql(sql, params=params)
