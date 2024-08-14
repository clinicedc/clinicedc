mysql_view: str = """
    select *, uuid() as `id`, now() as `created` from (
        select site_id, username, report_model, min(accessed) as `first_accessed`,
               max(accessed) as `last_accessed`, count(*) as `access_count`
        from edc_qareports_qareportlog
        group by username, report_model, site_id
    ) as A
    order by username, report_model
    """

pg_view: str = """
    select *, get_random_uuid() as id, now() as created (
        select site_id, username, report_model, min(accessed) as first_accessed,
               max(accessed) as last_accessed, count(*) as access_count
        from edc_qareports_qareportlog
        group by username, report_model, site_id
    ) as A
    order by username, report_model
"""

sqlite3_view = """
SELECT *, lower(
    hex(randomblob(4)) || '-' || hex(randomblob(2)) || '-' || '4' ||
    substr(hex( randomblob(2)), 2) || '-' ||
    substr('AB89', 1 + (abs(random()) % 4) , 1)  ||
    substr(hex(randomblob(2)), 2) || '-' ||
    hex(randomblob(6))
  ) as id, datetime() as created from (
        select site_id, username, report_model, min(accessed) as first_accessed,
               max(accessed) as last_accessed, count(*) as access_count
        from edc_qareports_qareportlog
        group by username, report_model, site_id
    ) as A
    order by username, report_model
"""


def get_view_definition() -> dict:
    return {
        "django.db.backends.mysql": mysql_view,
        "django.db.backends.postgresql": pg_view,
        "django.db.backends.sqlite3": sqlite3_view,
    }
