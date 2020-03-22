from django.apps import apps as django_apps

from .single_site import SingleSite


class InvalidSiteError(Exception):
    pass


def get_site_id(value, sites=None):
    """Returns the site_id given the site_name.
    """
    if not sites:
        site_model_cls = django_apps.get_model("edc_sites.edcsite")
        sites = [
            SingleSite(
                obj.id,
                obj.name,
                title=obj.title,
                description=obj.description,
                country=obj.country,
                country_code=obj.country_code,
                domain=obj.domain,
            )
            for obj in site_model_cls.objects.all()
        ]

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
