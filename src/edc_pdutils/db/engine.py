from sqlalchemy import create_engine


class Engine:

    def __init__(self, name=None, credentials=None):
        if name == 'mysql':
            self.engine = create_engine(
                f'mysql://{credentials.user}:{credentials.passwd}@'
                f'{credentials.host}:{credentials.port}/{credentials.dbname}')
        elif name == 'mssql':
            pass
