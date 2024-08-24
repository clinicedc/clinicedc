from .select_from import SelectFrom


def generate_subquery_for_missing_values(
    cases: list[dict[str:str, str:str, str:str]],
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
    select_from_list = []
    for case in cases:
        select_from = SelectFrom(**case)
        select_from_list.append(select_from.sql)
    if as_list:
        return select_from_list
    return " UNION ".join(select_from_list)
