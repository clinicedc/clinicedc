from edc_auth.site_auths import site_auths

from .auth_objects import LABELING, codenames


def update_site_auths():
    site_auths.add_group(*codenames, name=LABELING, no_delete=False)


update_site_auths()
