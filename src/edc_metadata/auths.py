from edc_auth.site_auths import site_auths
from edc_export.auth_objects import EXPORT

site_auths.update_group(
    "edc_metadata.export_crfmetadata", "edc_metadata.export_requisitionmetadata", name=EXPORT
)
