import numpy as np


class DfPrepper:
    def __init__(self, dataframe):
        self.dataframe = dataframe
        self.dataframe.fillna(value=np.nan, inplace=True)
        for column in list(self.dataframe.select_dtypes(
                include=['datetime64[ns, UTC]']).columns):
            self.dataframe[column] = self.dataframe[
                column].astype('datetime64[ns]')
