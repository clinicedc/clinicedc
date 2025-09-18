import json
import sys

from django.core.checks import Error
from django.db import OperationalError

from edc_sites.single_site import SingleSite
from edc_sites.site import SitesCheckError
from edc_sites.site import sites as site_sites
from edc_sites.utils import get_site_model_cls


def sites_check(app_configs, **kwargs):
    errors = []
    if "migrate" not in sys.argv and "makemigrations" not in sys.argv:
        try:
            compare_single_sites_with_db()
        except (SitesCheckError, OperationalError) as e:
            errors.append(
                Error(
                    e,
                    hint="Sites model is out-of-sync with edc_sites registry.",
                    obj=site_sites,
                    id="edc_sites.E001",
                )
            )
        if not site_sites.all():
            errors.append(
                Error(
                    "No sites have been registered",
                    id="edc_sites.E002",
                )
            )

    return errors


def compare_single_sites_with_db():
    """Checks the Site / SiteProfile tables are in sync"""
    if not get_site_model_cls().objects.all().exists():
        raise SitesCheckError("No sites have been imported. You need to run migrate")
    ids1 = sorted(list(site_sites.all()))
    ids2 = [x[0] for x in get_site_model_cls().objects.values_list("id").all().order_by("id")]
    if ids1 != ids2:
        raise SitesCheckError(
            f"Site table is out of sync. Got registered sites = {ids1}. "
            f"Sites in Sites model = {ids2}. Try running migrate."
        )
    for site_id, single_site in site_sites.all().items():
        site_obj = get_site_model_cls().objects.get(id=site_id)
        match_name_and_domain_or_raise(single_site, site_obj)
        match_country_and_country_code_or_raise(single_site, site_obj)
        match_languages_or_raise(single_site, site_obj)
        match_title_with_description_or_raise(single_site, site_obj)


def match_name_and_domain_or_raise(single_site: SingleSite, site_obj):
    for attr in ["name", "domain"]:
        value1 = getattr(single_site, attr)
        value2 = getattr(site_obj, attr)
        if value1 != value2:
            raise SitesCheckError(
                f"Site table is out of sync. Comparing {attr} of site `{site_obj.id}`. "
                "between the SingleSite and Site model. "
                f"Got `{value1}` != `{value2}`. Try running migrate."
            )


def match_country_and_country_code_or_raise(single_site: SingleSite, site_obj):
    for attr in ["country", "country_code"]:
        value1 = getattr(single_site, attr)
        value2 = getattr(site_obj.siteprofile, attr)
        if value1 != value2:
            raise SitesCheckError(
                f"Site table is out of sync. Checking {site_obj.id} {attr}. "
                f"Try running migrate. Got {value1} != {value2}"
            )


def match_languages_or_raise(single_site: SingleSite, site_obj):
    value1 = single_site.languages
    value2 = json.loads(site_obj.siteprofile.languages)
    if value1 != value2:
        raise SitesCheckError(
            f"Site table is out of sync. Checking {site_obj.id} "
            f"languages. Try running migrate. Got {value1} != {value2}"
        )


def match_title_with_description_or_raise(single_site: SingleSite, site_obj):
    value1 = site_obj.siteprofile.title
    value2 = single_site.description
    if value1 != value2:
        raise SitesCheckError(
            f"Site table is out of sync. Checking {site_obj.id} title/description. "
            f"Try running migrate. Got {value1} != {value2}"
        )
