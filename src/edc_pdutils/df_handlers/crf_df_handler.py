import pandas as pd

from ..constants import ACTION_ITEM_COLUMNS, SYSTEM_COLUMNS
from ..dialects import CrfDialect
from .df_handler import DfHandler


class CrfDfHandlerError(Exception):
    pass


class CrfDfHandler(DfHandler):
    crf_dialect_cls = CrfDialect
    # visit_tbl = None
    visit_column: str = "subject_visit_id"
    appointment_tbl: str = "edc_appointment_appointment"
    registered_subject_tbl: str = "edc_registration_registeredsubject"
    dialect_select_visit_and_related: str = "select_visit_and_related"

    action_item_columns = ACTION_ITEM_COLUMNS
    system_columns = SYSTEM_COLUMNS
    sort_by = ["subject_identifier", "visit_datetime"]
    exclude_export_columns = True
    exclude_system_columns = False
    exclude_columns = ["form_as_json"]

    def __init__(self, exclude_system_columns=None, **kwargs):
        self._df_visit_and_related = pd.DataFrame()
        self.crf_dialect = self.crf_dialect_cls(self)
        self.exclude_system_columns = exclude_system_columns or self.exclude_system_columns
        super().__init__(**kwargs)

    def prepare_dataframe(self, **kwargs):
        """Merges CRF dataframe with df_visit_and_related
        on visit_column.
        """
        if not self.visit_column:
            raise CrfDfHandlerError(
                f"visit column cannot be None. "
                f"See class attr 'visit_column' on {repr(self)}"
            )
        self.dataframe = pd.merge(
            left=self.dataframe,
            right=self.df_visit_and_related,
            how="left",
            on=self.visit_column,
            suffixes=("_notused", ""),
        )
        self.dataframe = self.dataframe[self.columns]

    @property
    def columns(self):
        """Returns a list of column names."""
        crf_columns = list(self.dataframe.columns)
        crf_columns.pop(crf_columns.index(self.visit_column))
        columns = list(self.df_visit_and_related.columns)
        columns.extend([c for c in crf_columns if c not in columns])
        columns = [col for col in columns if col not in self.exclude_columns]
        # "export_" columns
        if self.exclude_export_columns:
            columns = [col for col in columns if not col.startswith("export_")]
        if self.exclude_system_columns:
            columns = [col for col in columns if col not in self.system_columns]
        else:
            if [col for col in columns if col in self.action_item_columns]:
                # "action_item" columns, move to the end
                columns = [col for col in columns if col not in self.action_item_columns]
                columns.extend(self.action_item_columns)
            # "system" columns, move to the end
            columns = [col for col in columns if col not in self.system_columns]
            columns.extend(self.system_columns)
        return columns

    @property
    def df_visit_and_related(self):
        """Returns a dataframe of the crf_dialect's `select_visit_and_related`
        SQL statement.
        """
        if self._df_visit_and_related.empty:
            sql, params = getattr(self.crf_dialect, self.dialect_select_visit_and_related)
            self._df_visit_and_related = self.db.read_sql(sql, params=params)
        return self._df_visit_and_related
