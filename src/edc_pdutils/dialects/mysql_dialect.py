class MysqlDialect:
    def __init__(self, dbname=None):
        self.dbname = dbname

    def __repr__(self):
        return f"{self.__class__.__name__}({self.dbname})"

    @staticmethod
    def show_databases():
        sql = "SELECT SCHEMA_NAME AS `database` FROM INFORMATION_SCHEMA.SCHEMATA"
        return sql, None

    def show_tables(self, app_label=None):
        params = {"dbname": self.dbname, "app_label": f"{app_label}%"}
        select = "SELECT table_name FROM information_schema.tables"
        where = ["table_schema=%(dbname)s"]
        if app_label:
            where.append("table_name LIKE %(app_label)s ")
        sql = f'{select} WHERE {" AND ".join(where)}'
        return sql, params

    def show_tables_with_columns(self, app_label=None, column_names=None):
        column_names = "','".join(column_names)
        params = {
            "dbname": self.dbname,
            "app_label": f"{app_label}%",
            "column_names": column_names,
        }
        sql = (
            "SELECT DISTINCT table_name FROM information_schema.columns "
            f"WHERE table_schema=%(dbname)s "
            f"AND table_name LIKE %(app_label)s "
            f"AND column_name IN (%(column_names)s)"
        )
        return sql, params

    def show_tables_without_columns(self, app_label=None, column_names=None):
        column_names = "','".join(column_names)
        params = {
            "dbname": self.dbname,
            "app_label": f"{app_label}%",
            "column_names": column_names,
        }
        sql = (
            "SELECT DISTINCT table_name FROM information_schema.tables as T "
            "WHERE T.table_schema = %(dbname)s "
            "AND T.table_type = 'BASE TABLE' "
            "AND T.table_name LIKE %(app_label)s "
            "AND NOT EXISTS ("
            "SELECT * FROM INFORMATION_SCHEMA.COLUMNS C "
            "WHERE C.table_schema = T.table_schema "
            "AND C.table_name = T.table_name "
            "AND C.column_name IN (%(column_names)s))"
        )
        return sql, params

    @staticmethod
    def select_table(table_name=None):
        params = {}
        sql = f"select * from {table_name}"
        return sql, params

    @staticmethod
    def show_inline_tables(referenced_table_name=None):
        params = {"referenced_table_name": referenced_table_name}
        sql = (
            "SELECT DISTINCT referenced_table_name, table_name, "
            "column_name, referenced_column_name "
            "FROM information_schema.key_column_usage "
            "where referenced_table_name=%(referenced_table_name)s"
        )
        return sql, params
