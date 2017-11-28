from ..database import Database


class TableToDataframe:

    db_cls = Database

    def __init__(self, table_name=None, db_name=None, columns=None, limit=None,
                 df_handler_cls=None, **kwargs):
        self.db = self.db_cls(db_name=db_name, **kwargs)
        self.table_name = table_name
        df = self.db.select_table(table_name=self.table_name, limit=limit)
        if df_handler_cls:
            df_handler = self.df_handler_cls(
                dataframe=df, db=self.db,
                table_name=table_name, **kwargs)
            df = df_handler.dataframe
        if columns:
            self.dataframe = df.loc[:, columns]
        else:
            self.dataframe = df
