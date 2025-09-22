from edc_auth.site_auths import site_auths

from .auth_objects import (
    QA_REPORTS,
    QA_REPORTS_AUDIT,
    QA_REPORTS_AUDIT_ROLE,
    QA_REPORTS_ROLE,
    QA_REPORTS_SUPER_ROLE,
    qa_reports_codenames,
)


def update_site_auths() -> None:
    # groups
    site_auths.add_group(*qa_reports_codenames, name=QA_REPORTS)
    site_auths.add_group(*qa_reports_codenames, name=QA_REPORTS_AUDIT, view_only=True)

    # roles
    site_auths.add_role(QA_REPORTS, name=QA_REPORTS_ROLE)
    site_auths.add_role(QA_REPORTS, name=QA_REPORTS_SUPER_ROLE)
    site_auths.add_role(QA_REPORTS_AUDIT, name=QA_REPORTS_AUDIT_ROLE)


update_site_auths()
