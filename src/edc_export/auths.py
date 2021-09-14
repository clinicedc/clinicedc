from edc_auth.site_auths import site_auths

from .auth_objects import DATA_EXPORTER_ROLE, EXPORT, export_codenames

site_auths.add_group(*export_codenames, name=EXPORT)
site_auths.add_role(EXPORT, name=DATA_EXPORTER_ROLE)
