from django.contrib.sites.models import Site
from edc_sites import add_or_update_django_sites
from edc_sites.single_site import SingleSite

from edc_randomization.randomizer import Randomizer
from edc_randomization.site_randomizers import site_randomizers
from edc_randomization.tests.make_test_list import make_test_list

fqdn = "example.clinicedc.org"
all_sites = (
    SingleSite(10, "site_one", title="One", country="uganda", country_code="ug", fqdn=fqdn),
    SingleSite(20, "site_two", title="Two", country="uganda", country_code="ug", fqdn=fqdn),
    SingleSite(
        30, "site_three", title="Three", country="uganda", country_code="ug", fqdn=fqdn
    ),
    SingleSite(40, "site_four", title="Four", country="uganda", country_code="ug", fqdn=fqdn),
    SingleSite(50, "site_five", title="Five", country="uganda", country_code="ug", fqdn=fqdn),
)


class TestCaseMixin:
    import_randomization_list = False
    site_names = [x.name for x in all_sites]

    def setUp(self):
        super().setUp()
        add_or_update_django_sites(sites=all_sites)
        site_randomizers._registry = {}
        site_randomizers.register(Randomizer)

    def populate_list(
        self, randomizer_name=None, site_names=None, per_site=None, overwrite_site=None
    ):
        randomizer = site_randomizers.get(randomizer_name)
        make_test_list(
            full_path=randomizer.randomizationlist_path(),
            site_names=site_names or self.site_names,
            per_site=per_site,
        )
        randomizer.import_list(overwrite=True)
        if overwrite_site:
            site = Site.objects.get_current()
            randomizer.model_cls().objects.update(site_name=site.name)
