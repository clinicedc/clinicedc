from ..helper import Helper as BaseHelper
from .table_to_dataframe import TableToDataframe


class Helper(BaseHelper):
    to_dataframe_cls = TableToDataframe
