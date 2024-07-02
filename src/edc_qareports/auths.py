from edc_auth.site_auths import site_auths

from .auth_objects import (
    QA_REPORTS,
    QA_REPORTS_AUDIT,
    QA_REPORTS_AUDIT_ROLE,
    QA_REPORTS_ROLE,
    custom_codename_tuples,
    qa_reports_codenames,
)

site_auths.add_custom_permissions_tuples(
    model="edc_qareports.edcpermissions", codename_tuples=custom_codename_tuples
)


# groups
site_auths.add_group(*qa_reports_codenames, name=QA_REPORTS)
site_auths.add_group(*qa_reports_codenames, name=QA_REPORTS_AUDIT, view_only=True)


# roles
site_auths.add_role(QA_REPORTS, name=QA_REPORTS_ROLE)
site_auths.add_role(QA_REPORTS_AUDIT, name=QA_REPORTS_AUDIT_ROLE)
