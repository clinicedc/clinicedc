from dataclasses import dataclass

from .crf_case import CrfCase
from .requisition_subquery import RequisitionSubquery


@dataclass(kw_only=True)
class RequisitionCase(CrfCase):
    panel: str = None
    subjectrequisition_dbtable: str | None = None
    panel_dbtable: str | None = None

    @property
    def sql(self):
        sql = RequisitionSubquery(**self.__dict__).sql
        return sql.format(panel=self.panel)
