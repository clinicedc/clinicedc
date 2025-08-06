from edc_auth.site_auths import site_auths

from .auth_objects import EDC_FACILITY, EDC_FACILITY_SUPER, EDC_FACILITY_VIEW, codenames

site_auths.add_group(*codenames, name=EDC_FACILITY_VIEW, view_only=True)
site_auths.add_group(*codenames, name=EDC_FACILITY, no_delete=True)
site_auths.add_group(*codenames, name=EDC_FACILITY_SUPER)
