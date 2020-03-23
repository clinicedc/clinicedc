import os

from django.apps import apps as django_apps
from django.test import TestCase, tag
from django.test.utils import override_settings
from django.conf import settings
from edc_sites import add_or_update_django_sites
from edc_sites.tests import SiteTestCaseMixin
from multisite import SiteID

from ..import_holidays import import_holidays
from ..system_checks import holiday_path_check, holiday_country_check


class TestSystemChecks(SiteTestCaseMixin, TestCase):
    def setUp(self):
        add_or_update_django_sites(sites=self.default_sites)

    @override_settings(SITE_ID=SiteID(default=10),)
    def test_(self):
        # app_configs = django_apps.get_app_configs()
        holiday_path_check(app_configs=None)

    @override_settings(
        HOLIDAY_FILE=None, SITE_ID=SiteID(default=10),
    )
    def test_file(self):
        app_configs = django_apps.get_app_configs()
        errors = holiday_path_check(app_configs=app_configs)
        self.assertIn("edc_facility.001", [error.id for error in errors])

    @override_settings(
        HOLIDAY_FILE=os.path.join(
            settings.BASE_DIR, "edc_facility", "tests", "blah.csv"
        ),
        SITE_ID=SiteID(default=10),
    )
    def test_bad_path(self):
        app_configs = django_apps.get_app_configs()
        errors = holiday_path_check(app_configs=app_configs)
        self.assertIn("edc_facility.002", [error.id for error in errors])

    @override_settings(
        HOLIDAY_FILE=os.path.join(
            settings.BASE_DIR, "edc_facility", "tests", "holidays.csv"
        ),
        SITE_ID=SiteID(default=60),
    )
    def test_no_country(self):
        app_configs = django_apps.get_app_configs()
        errors = holiday_country_check(app_configs=app_configs)
        self.assertIn("edc_facility.004", [error.id for error in errors])

    @override_settings(
        HOLIDAY_FILE=os.path.join(
            settings.BASE_DIR, "edc_facility", "tests", "holidays.csv"
        ),
        SITE_ID=SiteID(default=60),
    )
    def test_unknown_country(self):
        import_holidays()
        app_configs = django_apps.get_app_configs()
        errors = holiday_country_check(app_configs=app_configs)
        self.assertIn("edc_facility.004", [error.id for error in errors])
