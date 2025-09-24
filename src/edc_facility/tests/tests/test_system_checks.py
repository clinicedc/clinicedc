from clinicedc_tests.mixins import SiteTestCaseMixin
from clinicedc_tests.sites import all_sites
from django.apps import apps as django_apps
from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings, tag
from multisite import SiteID

from edc_facility.import_holidays import import_holidays
from edc_facility.system_checks import holiday_country_check, holiday_path_check
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites


@tag("facility")
@override_settings(SITE_ID=10)
class TestSystemChecks(SiteTestCaseMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()

    @override_settings(
        SITE_ID=SiteID(default=10),
    )
    def test_(self):
        holiday_path_check(app_configs=None)

    @override_settings(
        HOLIDAY_FILE=None,
        SITE_ID=10,
    )
    def test_file(self):
        app_configs = django_apps.get_app_configs()
        errors = holiday_path_check(app_configs=app_configs)
        self.assertIn("edc_facility.E001", [error.id for error in errors])

    @override_settings(
        HOLIDAY_FILE=settings.BASE_DIR / "tests" / "blah.csv",
        SITE_ID=10,
    )
    def test_bad_path(self):
        app_configs = django_apps.get_app_configs()
        errors = holiday_path_check(app_configs=app_configs)
        self.assertIn("edc_facility.W001", [error.id for error in errors])

    @override_settings(
        HOLIDAY_FILE=settings.BASE_DIR / "tests" / "holidays_extra_mozambique.csv",
        SITE_ID=60,
    )
    def test_unknown_country(self):
        import_holidays()
        app_configs = django_apps.get_app_configs()
        errors = holiday_country_check(app_configs=app_configs)
        self.assertIn("edc_facility.W002", [error.id for error in errors])
