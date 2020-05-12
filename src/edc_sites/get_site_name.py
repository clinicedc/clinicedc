from .get_site_id import get_sites_from_model, InvalidSiteError


def get_site_name(value, sites=None):
    """Returns the site_name given the site_id.
    """
    if not sites:
        sites = get_sites_from_model()

    try:
        site_name = [site for site in sites if site.site_id == value][0].name
    except IndexError:
        site_ids = [site.site_id for site in sites]
        raise InvalidSiteError(
            f"Invalid site. Got '{value}'. Expected one of " f"{site_ids}."
        )
    return site_name
