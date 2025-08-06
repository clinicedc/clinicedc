from __future__ import annotations

from typing import TYPE_CHECKING

from .subquery import Subquery

if TYPE_CHECKING:
    from .qa_case import QaCase


def subquery_from_dict(
    cases: list[dict[str:str, str:str, str:str] | QaCase],
    as_list: bool | None = False,
) -> str | list:
    """Returns an SQL select statement as a union of the select
    statements of each case.

    args:
     cases = [{
         "label_lower": "my_app.hivhistory",
         "dbtable": "my_app_hivhistory",
         "field": "hiv_init_date",
         "label": "missing HIV initiation date",
         "list_tables": [(list_field, list_dbtable, alias), ...],
         }, ...]

         Note: `list_field` is the CRF id field, for example:
            left join <list_dbtable> as <alias> on crf.<list_field>=<alias>.id
    """
    subqueries = []
    for case in cases:
        try:
            subquery = case.sql
        except AttributeError:
            subquery = Subquery(**case).sql
        subqueries.append(subquery)
    if as_list:
        return subqueries
    return " UNION ".join(subqueries)
