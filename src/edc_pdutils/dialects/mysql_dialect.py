
class MysqlDialect:

    def __init__(self, dbname=None):
        self.dbname = dbname

    def show_databases(self):
        sql = 'SELECT SCHEMA_NAME AS `database` FROM INFORMATION_SCHEMA.SCHEMATA'
        return sql, None

    def show_tables(self, app_label=None):
        params = {'dbname': self.dbname, 'app_label': f'{app_label}%%'}
        select = ('SELECT table_name FROM information_schema.tables')
        where = [f'table_schema=%(dbname)s']
        if app_label:
            where.append(f'table_name LIKE %(app_label)s')
        sql = f'{select} WHERE {" AND ".join(where)}'
        return sql, params

    def show_tables_with_columns(self, app_label=None, column_names=None):
        column_names = '\',\''.join(column_names)
        params = {
            'dbname': self.dbname,
            'app_label': f'{app_label}%%',
            'column_names': column_names}
        sql = (
            'SELECT DISTINCT table_name FROM information_schema.columns '
            f'WHERE table_schema=%(dbname)s '
            f'AND table_name LIKE %(app_label)s '
            f'AND column_name IN (%(column_names)s)')
        return sql, params

    def show_tables_without_columns(self, app_label=None, column_names=None):
        column_names = '\',\''.join(column_names)
        params = {
            'dbname': self.dbname,
            'app_label': f'{app_label}%%',
            'column_names': column_names}
        sql = ('SELECT DISTINCT table_name FROM information_schema.tables as T '
               f'WHERE T.table_schema = %(dbname)s '
               f'AND T.table_type = \'BASE TABLE\' '
               f'AND T.table_name LIKE %(app_label)s '
               'AND NOT EXISTS ('
               'SELECT * FROM INFORMATION_SCHEMA.COLUMNS C '
               'WHERE C.table_schema = T.table_schema '
               'AND C.table_name = T.table_name '
               f'AND C.column_name IN (%(column_names)s))')
        return sql, params

    def select_table(self, table_name=None):
        params = {'table_name': table_name}
        sql = f'select * from {table_name}'
        return sql, params

    def show_inline_tables(self, referenced_table_name=None):
        params = {'referenced_table_name': referenced_table_name}
        sql = (f'SELECT DISTINCT referenced_table_name, table_name, '
               'column_name, referenced_column_name '
               f'FROM information_schema.key_column_usage '
               f'where referenced_table_name=%(referenced_table_name)s')
        return sql, params
