create view qa_report_log_summary_view as (
    select *, uuid() as 'id', now() as 'created' from (
        select site_id, username, report_model, min(accessed) as first_accessed,
               max(accessed) as last_accessed, count(*) as access_count
        from edc_qareports_qareportlog
        group by username, report_model, site_id
    ) as A
    order by username, report_model
)
