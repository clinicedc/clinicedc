from dataclasses import dataclass, field
from string import Template


class CrfSubqueryError(Exception):
    pass


@dataclass(kw_only=True)
class CrfSubquery:
    label: str = None
    label_lower: str = None
    dbtable: str = None
    fld_name: str | None = None
    subjectvisit_dbtable: str | None = None
    where: str | None = None
    list_tables: list[tuple[str, str, str]] | None = field(default_factory=list)
    template: Template = field(
        init=False,
        default=Template(
            "select v.subject_identifier, crf.id as original_id, crf.subject_visit_id, "
            "crf.report_datetime, crf.site_id, v.visit_code, "
            "v.visit_code_sequence, v.schedule_name, crf.modified, "
            "'${label_lower}' as label_lower, "
            "'${label}' as label, count(*) as records "
            "from ${dbtable} as crf "
            "left join ${subjectvisit_dbtable} as v on v.id=crf.subject_visit_id "
            "${left_joins} "
            "where ${where} "
            "group by v.subject_identifier, crf.subject_visit_id, crf.report_datetime, "
            "crf.site_id, v.visit_code, v.visit_code_sequence, v.schedule_name, crf.modified"
        ),
    )

    def __post_init__(self):
        # default where statement if not provided and have fld_name.
        if self.where is None and self.fld_name:
            self.where = f"crf.{self.fld_name} is null"
        if not self.label_lower:
            raise CrfSubqueryError("label_lower is required")
        if not self.subjectvisit_dbtable:
            self.subjectvisit_dbtable = f"{self.label_lower.split('.')[0]}_subjectvisit"

    @property
    def left_joins(self) -> str:
        """Add list tbls to access list cols by 'name' instead of 'id'"""
        left_join = []
        for opts in self.list_tables or []:
            list_field, list_dbtable, alias = opts
            left_join.append(
                f"left join {list_dbtable} as {alias} on crf.{list_field}={alias}.id"
            )
        return " ".join(left_join)

    @property
    def sql(self):
        opts = {k: v for k, v in self.__dict__.items() if v is not None}
        opts.update(left_joins=self.left_joins)
        try:
            sql = self.template.substitute(**opts).replace(";", "")
        except KeyError as e:
            raise CrfSubqueryError(e)
        return sql
