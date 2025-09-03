from edc_randomization.randomizer import Randomizer
from edc_randomization.site_randomizers import site_randomizers
from edc_sites.single_site import SingleSite
from edc_sites.site import sites
from edc_sites.utils import add_or_update_django_sites
from .utils import populate_randomization_list_for_tests

suffix = "example.clinicedc.org"
all_sites = (
    SingleSite(
        10,
        "site_one",
        title="One",
        country="uganda",
        country_code="ug",
        domain=f"site_one.{suffix}",
    ),
    SingleSite(
        20,
        "site_two",
        title="Two",
        country="uganda",
        country_code="ug",
        domain=f"site_two.{suffix}",
    ),
    SingleSite(
        30,
        "site_three",
        title="Three",
        country="uganda",
        country_code="ug",
        domain=f"site_three.{suffix}",
    ),
    SingleSite(
        40,
        "site_four",
        title="Four",
        country="uganda",
        country_code="ug",
        domain=f"site_four.{suffix}",
    ),
    SingleSite(
        50,
        "site_five",
        title="Five",
        country="uganda",
        country_code="ug",
        domain=f"site_five.{suffix}",
    ),
)


class TestCaseMixin:
    import_randomization_list = False
    site_names = [x.name for x in all_sites]

    @classmethod
    def setUpTestData(cls):
        sites.initialize()
        sites.register(*all_sites)
        add_or_update_django_sites()

    def setUp(self):
        super().setUp()
        site_randomizers._registry = {}
        site_randomizers.register(Randomizer)

    def populate_list(
        self, randomizer_name=None, site_names=None, per_site=None, overwrite_site=None
    ):
        site_names = site_names or self.site_names
        populate_randomization_list_for_tests(
            randomizer_name=randomizer_name,
            site_names=site_names,
            per_site=per_site,
            overwrite_site=overwrite_site,
        )
