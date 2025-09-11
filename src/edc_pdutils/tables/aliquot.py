from copy import copy

import pandas as pd

from ..constants import SYSTEM_COLUMNS
from ..mappings import yes_no
from .table import Table


class Aliquot(Table):
    default_columns = None
    requisition_columns = [
        "requisition_identifier",
        "panel_name",
        "requisition_datetime",
        "drawn_datetime",
        "gender",
        "dob",
        "study_site",
        "study_site_name",
        "visit_code",
        "visit_datetime",
        "visit_date",
    ]

    def prepare(self, df_requisition=None, requisition_columns=None, **kwargs):
        self.requisition_columns = requisition_columns or self.requisition_columns
        self.dataframe["aliquot_datetime"] = self.helper.to_local_datetime(
            self.dataframe["aliquot_datetime"]
        )
        self.dataframe["aliquot_date"] = self.dataframe["aliquot_datetime"].dt.normalize()

        # drop sys and other unwanted columns
        base_cols = copy(SYSTEM_COLUMNS)
        base_cols.append("id")
        base_cols.pop(base_cols.index("hostname_created"))
        base_cols = base_cols + ["slug", "comment", "shipped"]
        self.dataframe = self.dataframe.drop(base_cols, axis=1)

        # add column to indicate missing requisitions, remap columns
        self.dataframe["missing_requisition"] = self.missing_requisition(df_requisition)
        self.dataframe["is_primary"] = self.dataframe["is_primary"].map(
            yes_no, na_action="ignore"
        )
        self.dataframe["medium"] = self.dataframe["medium"].str.lower()
        self.dataframe["parent_identifier"] = self.dataframe.apply(
            lambda row: self.fix_parent_identifier(row["parent_identifier"]), axis=1
        )
        self.dataframe = pd.merge(
            self.dataframe,
            df_requisition[self.requisition_columns],
            on="requisition_identifier",
            how="left",
        )
        self.dataframe = self.dataframe[self.reordered_columns]

    @property
    def reordered_columns(self):
        columns = [
            col
            for col in list(self.dataframe.columns)
            if col
            not in [
                "hostname_created",
                "subject_identifier",
                "gender",
                "dob",
                "visit_code",
                "visit_datetime",
                "visit_date",
            ]
        ]
        columns.insert(0, "visit_code")
        columns.insert(0, "visit_date")
        columns.insert(0, "visit_datetime")
        columns.insert(0, "dob")
        columns.insert(0, "gender")
        columns.insert(0, "subject_identifier")
        columns.append("hostname_created")
        return columns

    def fix_parent_identifier(self, value):
        if value:
            value = value.replace("(", "").replace(")", "").replace("'", "").replace(",", "")
        return value

    def missing_requisition(self, df_requisition=None):
        """Returns a Series with True for rows missing a requisition."""
        missing = pd.merge(
            self.dataframe,
            df_requisition[self.requisition_columns],
            on="requisition_identifier",
            how="left",
        )
        return missing["panel_name"].isnull()
