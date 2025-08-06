from dataclasses import dataclass, field
from string import Template

from edc_constants.constants import YES

from .crf_subquery import CrfSubquery


class RequisitionSubqueryError(Exception):
    pass


@dataclass(kw_only=True)
class RequisitionSubquery(CrfSubquery):
    """Generate a SELECT query returning requisitions where
    is_drawn=Yes for a given panel but results have not been captured
    in the result CRF.

    For example requisition exists for panel FBC but results_fbc
    CRF does not exist.
    """

    panel: str = None
    subjectrequisition_dbtable: str | None = None
    panel_dbtable: str | None = None
    requisition_id_field: str | None = None
    template: str = field(
        init=False,
        default=Template(
            "select req.subject_identifier, req.id as original_id, "  # nosec B608
            "req.subject_visit_id, req.report_datetime, req.site_id, v.visit_code, "
            "v.visit_code_sequence, "
            "v.schedule_name, req.modified, '${label_lower}' as label_lower, "
            "'${label}' as label, count(*) as records "
            "from ${subjectrequisition_dbtable} as req "
            "left join ${dbtable} as crf on req.id=crf.${requisition_id_field} "
            "left join ${subjectvisit_dbtable} as v on v.id=req.subject_visit_id "
            "${left_joins} "
            "left join ${panel_dbtable} as panel on req.panel_id=panel.id "
            f"where panel.name='${{panel}}' and req.is_drawn='{YES}' and crf.id is null "
            "group by req.id, req.subject_identifier, req.subject_visit_id, "
            "req.report_datetime, req.site_id, v.visit_code, v.visit_code_sequence, "
            "v.schedule_name, req.modified"
        ),
    )

    def __post_init__(self):
        # default where statement if not provided and have fld_name.
        if self.where is None and self.fld_name:
            self.where = f"crf.{self.fld_name} is null"
        if not self.label_lower:
            raise RequisitionSubqueryError("label_lower is required")
        if not self.subjectvisit_dbtable:
            self.subjectvisit_dbtable = f"{self.label_lower.split('.')[0]}_subjectvisit"
        if not self.subjectrequisition_dbtable:
            self.subjectrequisition_dbtable = (
                f"{self.label_lower.split('.')[0]}_subjectrequisition"
            )
        if not self.panel_dbtable:
            self.panel_dbtable = "edc_lab_panel"
        if not self.requisition_id_field:
            self.requisition_id_field = "requisition_id"
