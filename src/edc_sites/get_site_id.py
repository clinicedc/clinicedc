from .get_sites_from_model import get_sites_from_model


class InvalidSiteError(Exception):
    pass


def get_site_id(value, sites=None):
    """Returns the site_id given the site_name"""
    if not sites:
        sites = get_sites_from_model()

    try:
        site_id = [site for site in sites if site.name == value][0].site_id
    except IndexError:
        try:
            site_id = [site for site in sites if site.title == value][0].site_id
        except IndexError:
            site_ids = [site.site_id for site in sites]
            site_names = [site.name for site in sites]
            raise InvalidSiteError(
                f"Invalid site. Got '{value}'. Expected one of "
                f"{site_ids} or {site_names}."
            )
    return site_id
