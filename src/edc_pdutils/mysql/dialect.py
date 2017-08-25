class Dialect:

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
