from edc_auth.site_auths import site_auths

from .auth_objects import PYLABELS, codenames

site_auths.add_group(*codenames, name=PYLABELS, no_delete=False)
