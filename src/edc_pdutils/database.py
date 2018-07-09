import sys
import pandas as pd
import numpy as np

from django.conf import settings
from django.db import connection
from uuid import UUID

from .dialects import MysqlDialect


class DatabaseNameError(Exception):
    pass


class Database:

    dialect_cls = MysqlDialect
    lowercase_columns = True
    DATABASES_NAME = 'default'

    def __init__(self, **kwargs):
        self._database = None
        self._tables = pd.DataFrame()
        self.dialect = self.dialect_cls(dbname=self.database)

    @property
    def database(self):
        """Returns the database name.
        """
        if not self._database:
            filename = settings.DATABASES.get(self.DATABASES_NAME).get(
                'OPTIONS').get('read_default_file')
            if 'test' in sys.argv:
                self._database = connection.settings_dict['TEST']['NAME']
            else:
                self._database = connection.settings_dict['NAME']
                if not self._database:
                    with open(filename, 'r') as f:
                        for line in [line for line in f if '#' not in line]:
                            if 'database' in line:
                                self._database = line.split('=')[1].strip()
            if not self._database:
                raise DatabaseNameError(
                    f'Unable to determine the DB name from settings.DATABASES. '
                    f'Got NAME={self.DATABASES_NAME}, read_default_file={filename}.')
        return self._database

    def read_sql(self, sql, params=None):
        """Returns a dataframe. A simple wrapper for pd.read_sql().
        """
        return pd.read_sql(sql, connection, params=params)

    def show_databases(self):
        """Returns a dataframe of database names in the schema.
        """
        sql, params = self.dialect.show_databases()
        return self.read_sql(sql, params=params)

    def select_table(self, table_name=None, lowercase_columns=None, uuid_columns=None,
                     limit=None):
        """Returns a dataframe of a table.

        Note: UUID columns are stored as strings (uuid.hex) and need
        to be converted from string to UUID if to match the
        rendering of the same column by a Django model class.
        """
        uuid_columns = uuid_columns or []
        lowercase_columns = lowercase_columns or self.lowercase_columns
        sql, params = self.dialect.select_table(table_name)
        if limit:
            sql = f'{sql} LIMIT {int(limit)}'
        df = self.read_sql(sql, params=params)
        if lowercase_columns:
            columns = {col: col.lower() for col in list(df.columns)}
            df.rename(columns=columns, inplace=True)
        for col in uuid_columns:
            df[col] = df.apply(
                lambda row: str(
                    UUID(row[col])) if row[col] else np.nan,
                axis=1)
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
