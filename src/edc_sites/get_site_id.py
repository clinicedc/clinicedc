from django.apps import apps as django_apps


class InvalidSiteError(Exception):
    pass


def get_site_id(value, sites=None):
    """Expects sites list has elements of format
    (SITE_ID(int), site_name(char), site_long_name(char)).
    """
    if not sites:
        EdcSite = django_apps.get_model("edc_sites.edcsite")
        sites = [(obj.id, obj.name, obj.title)
                 for obj in EdcSite.objects.all()]

    try:
        site_id = [site for site in sites if site[1] == value][0][0]
    except IndexError:
        try:
            site_id = [site for site in sites if site[2] == value][0][0]
        except IndexError:
            site_ids = [site[1] for site in sites]
            site_names = [site[2] for site in sites]
            raise InvalidSiteError(
                f"Invalid site. Got '{value}'. Expected one of "
                f"{site_ids} or {site_names}."
            )
    return site_id
