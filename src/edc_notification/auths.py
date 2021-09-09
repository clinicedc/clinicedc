from edc_auth.default_role_names import ACCOUNT_MANAGER_ROLE
from edc_auth.site_auths import site_auths

from .auth_objects import NOTIFICATION, codenames

site_auths.add_group(*codenames, name=NOTIFICATION)
site_auths.update_role(NOTIFICATION, name=ACCOUNT_MANAGER_ROLE)
