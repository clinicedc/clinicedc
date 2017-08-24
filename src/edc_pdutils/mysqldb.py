import pandas as pd
import numpy as np

from django.core.management.color import color_style
from sqlalchemy import create_engine

style = color_style()


class DbConnectionError(Exception):
    pass


class Engine:

    def __init__(self, name=None, credentials=None):
        if name == 'mysql':
            self.engine = create_engine(
                f'mysql://{credentials.user}:{credentials.passwd}@'
                f'{credentials.host}:{credentials.port}/{credentials.dbname}')
        elif name == 'mssql':
            pass


class Credentials:

    user = None
    passwd = None
    host = None
    port = None
    dbname = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if getattr(self, k) is None:
                setattr(self, k, v)


class MysqlDialect:

    def __init__(self, dbname=None):
        self.dbname = dbname

    def show_databases(self):
        return 'SELECT SCHEMA_NAME AS `database` FROM INFORMATION_SCHEMA.SCHEMATA'

    def show_tables(self, app_label=None):
        select = ('SELECT table_name FROM information_schema.tables')
        where = [f'table_schema=\'{self.dbname}\'']
        if app_label:
            where.append(f'table_name LIKE \'{app_label}%%\'')
        return f'{select} WHERE {" AND ".join(where)}'

    def show_tables_with_columns(self, app_label=None, column_names=None):
        column_names = '\',\''.join(column_names)
        return (
            'SELECT DISTINCT table_name FROM information_schema.columns '
            f'WHERE table_schema=\'{self.dbname}\' '
            f'AND table_name LIKE \'{app_label}%%\' '
            f'AND column_name IN (\'{column_names}\')')

    def select_table(self, table_name=None):
        return f'select * from {table_name}'


class MysqlDb(object):

    engine_cls = Engine
    credentials_cls = Credentials
    dialect_cls = MysqlDialect

    def __init__(self, credentials=None, engine_name='mysql', **kwargs):
        if not credentials:
            credentials = self.credentials_cls(**kwargs)
        self.engine_name = engine_name or 'mysql'
        self.database = credentials.dbname
        self.dialect = self.dialect_cls(dbname=credentials.dbname)
        self.verfy_dbname(credentials=credentials)
        self.engine = self.engine_cls(
            name=engine_name, credentials=credentials).engine
        self._tables = pd.DataFrame()

    def verfy_dbname(self, credentials=None):
        dbname = credentials.dbname
        credentials.dbname = 'mysql'
        self.engine = self.engine_cls(
            name=self.engine_name, credentials=credentials).engine
        df = self.show_databases()
        databases = list(df.database)
        if dbname not in databases:
            raise DbConnectionError(
                f'Unknown database {dbname}. Available databases are {", ".join(databases)}')
        else:
            credentials.dbname = dbname

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
        return self.format_df(df=df)

    def format_df(self, df=None):
        df.fillna(value=np.nan, inplace=True)
        for column in list(df.select_dtypes(include=['datetime64[ns, UTC]']).columns):
            df[column] = df[column].astype('datetime64[ns]')
        return df
