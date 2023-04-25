from edc_auth.site_auths import site_auths
from edc_auth.utils import remove_default_model_permissions_from_edc_permissions

from .auth_objects import DATA_EXPORTER_ROLE, EXPORT, EXPORT_PII, export_codenames

site_auths.add_post_update_func(
    "edc_export",
    remove_default_model_permissions_from_edc_permissions,
)

site_auths.add_custom_permissions_tuples(
    model="edc_export.edcpermissions",
    codename_tuples=[
        (
            "edc_export.export_visitschedule",
            "Can export the visit schedule",
        ),
        (
            "edc_export.view_export_dashboard",
            "Can view export dashboard",
        ),
        (
            "edc_export.export_subjectschedulehistory",
            "Can export subject schedule history",
        ),
        (
            "edc_export.export_pii",
            "Can export PII",
        ),
    ],
)


site_auths.add_group(*export_codenames, name=EXPORT)
site_auths.add_role(EXPORT, name=DATA_EXPORTER_ROLE)
site_auths.add_group("edc_export.export_pii", name=EXPORT_PII)
