from edc_auth.site_auths import site_auths
from edc_screening.auth_objects import SCREENING, SCREENING_SUPER

from .auth_objects import codenames

site_auths.update_group(*codenames, name=SCREENING, no_delete=True)
site_auths.update_group(*codenames, name=SCREENING_SUPER)
