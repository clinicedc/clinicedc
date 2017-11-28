from edc_pdutils.df_handlers.crf_df_handler import CrfDfHandler


class NonCrfDfHandler(CrfDfHandler):

    sort_by = None

    def prepare_dataframe(self, **kwargs):
        columns = [col for col in self.columns if col in self.dataframe.columns]
        self.dataframe = self.dataframe.loc[:, columns]

    @property
    def columns(self):
        """Returns a list of column names.
        """
        columns = list(self.dataframe.columns)
        # "export_" columns
        if self.exclude_export_columns:
            columns = [col for col in columns if not col.startswith('export_')]
        # "system" columns, move to the end
        if not self.exclude_system_columns:
            columns = [col for col in columns if col not in self.system_columns]
            columns.extend(self.system_columns)
        return columns
