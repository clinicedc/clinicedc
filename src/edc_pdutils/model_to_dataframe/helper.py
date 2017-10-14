from ..helper import Helper as BaseHelper
from .model_to_dataframe import ModelToDataframe


class Helper(BaseHelper):

    to_dataframe_cls = ModelToDataframe
