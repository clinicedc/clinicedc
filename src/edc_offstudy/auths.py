from edc_auth.auth_objects import AUDITOR_ROLE
from edc_auth.site_auths import site_auths

from edc_offstudy.auth_objects import (
    OFFSTUDY,
    OFFSTUDY_EXPORT,
    OFFSTUDY_VIEW,
    codenames,
)

site_auths.add_group(*codenames, name=OFFSTUDY)
site_auths.add_group(*codenames, name=OFFSTUDY_VIEW, view_only=True)
site_auths.add_group(*codenames, name=OFFSTUDY_EXPORT, convert_to_export=True)
site_auths.update_role(OFFSTUDY_VIEW, name=AUDITOR_ROLE)
