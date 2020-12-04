from edc_sites.get_sites_from_model import get_sites_from_model


class SiteDoesNotExist(Exception):
    pass


def get_site_by_attr(attrname, value, sites=None):
    if not sites:
        sites = get_sites_from_model()
    try:
        site = [site for site in sites if getattr(site, attrname) == value][0]
    except IndexError:
        raise SiteDoesNotExist(f"No site exists with `{attrname}`=={value}.")
    return site
