from dataclasses import dataclass, field


@dataclass(kw_only=True)
class Subquery:
    label: str = None
    label_lower: str = None
    dbtable: str = None
    fld_name: str | None = None
    where: str | None = None
    list_tables: list[tuple[str, str, str]] | None = field(default_factory=list)
    template: str = field(
        init=False,
        default="select v.subject_identifier, crf.id as original_id, crf.subject_visit_id, crf.report_datetime, crf.site_id, v.visit_code, v.visit_code_sequence, v.schedule_name, crf.modified, '{label_lower}' as label_lower, '{label}' as label, count(*) as records from {dbtable} as crf left join meta_subject_subjectvisit as v on v.id=crf.subject_visit_id {left_joins} where {where} group by v.subject_identifier, crf.subject_visit_id, crf.report_datetime, crf.site_id, v.visit_code, v.visit_code_sequence, v.schedule_name, crf.modified",  # noqa
    )
    sql: str | None = field(init=False, default=None)

    def __post_init__(self):
        if self.where is None:
            self.where = f"crf.{self.fld_name} is null"
        self.sql = self.template.format(
            label=self.label,
            label_lower=self.label_lower,
            dbtable=self.dbtable,
            where=self.where,
            left_joins=self.left_joins,
        )
        self.sql = self.sql.replace(";", "")

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
