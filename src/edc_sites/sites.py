"""Default sites module.

Define ``sites.py`` in your own module and set EDC_SITES_MODULE_NAME
to the name of that module.

"""
from django.conf import settings

from edc_sites.single_site import SingleSite

default_country = getattr(settings, "EDC_SITES_DEFAULT_COUNTRY", "botswana")
default_country_code = getattr(settings, "EDC_SITES_DEFAULT_COUNTRY_CODE", "bw")
default_domain = getattr(settings, "EDC_SITES_DEFAULT_DOMAIN", "localhost")

all_sites = {
    default_country
    or "site": [
        SingleSite(
            1,
            settings.APP_NAME,
            country=default_country,
            country_code=default_country_code,
            domain=default_domain,
        ),
    ],
}
