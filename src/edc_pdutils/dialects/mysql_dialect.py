import re

from sqlalchemy import TextClause, text


class MysqlDialectError(Exception):
    pass


class MysqlDialect:
    def __init__(self, dbname=None):
        self.dbname = dbname

    def __repr__(self):
        return f"{self.__class__.__name__}({self.dbname})"

    @staticmethod
    def show_databases() -> tuple[TextClause, None]:
        sql = text("SELECT SCHEMA_NAME AS 'database' FROM INFORMATION_SCHEMA.SCHEMATA")
        return sql, None

    def show_tables(self, app_label: str = None) -> tuple[TextClause, dict]:
        params = {"dbname": self.dbname}
        select = "SELECT table_name FROM information_schema.tables"
        where = ["table_schema=:dbname"]
        if app_label:
            where.append("table_name LIKE :app_label ")
            params.update({"app_label": f"{app_label}%"})
        sql = text(f'{select} WHERE {" AND ".join(where)}')
        return sql, params

    def show_tables_with_columns(
        self, app_label: str = None, column_names: list[str] = None
    ) -> tuple[TextClause, dict]:
        column_names = "','".join(column_names)
        params = {
            "dbname": self.dbname,
            "app_label": f"{app_label}%",
            "column_names": column_names,
        }
        sql = text(
            "SELECT DISTINCT table_name FROM information_schema.columns "
            "WHERE table_schema=:dbname "
            "AND table_name LIKE :app_label "
            "AND column_name IN (:column_names)"
        )
        return sql, params

    def show_tables_without_columns(
        self, app_label: str = None, column_names: list[str] = None
    ) -> tuple[TextClause, dict]:
        column_names = "','".join(column_names)
        params = {
            "dbname": self.dbname,
            "app_label": f"{app_label}%",
            "column_names": column_names,
        }
        sql = text(
            "SELECT DISTINCT table_name FROM information_schema.tables as T "
            "WHERE T.table_schema = :dbname "
            "AND T.table_type = 'BASE TABLE' "
            "AND T.table_name LIKE :app_label "
            "AND NOT EXISTS ("
            "SELECT * FROM INFORMATION_SCHEMA.COLUMNS C "
            "WHERE C.table_schema = T.table_schema "
            "AND C.table_name = T.table_name "
            "AND C.column_name IN (:column_names)"
        )
        return sql, params

    @staticmethod
    def select_table(table_name: str = None) -> tuple[TextClause, dict]:
        if not re.match(r"^[A-Za-z0-9]+(?:_[A-Za-z0-9]+)*$", table_name):
            raise MysqlDialectError(f"Invalid table_name. Got {table_name}")
        params = {}
        sql = text(f"select * from {table_name}")  # nosec B608
        return sql, params

    @staticmethod
    def show_inline_tables(referenced_table_name: str = None) -> tuple[TextClause, dict]:
        params = {"referenced_table_name": referenced_table_name}
        sql = text(
            "SELECT DISTINCT referenced_table_name, table_name, "
            "column_name, referenced_column_name "
            "FROM information_schema.key_column_usage "
            "where referenced_table_name=:referenced_table_name"
        )
        return sql, params
