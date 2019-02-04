import os

from django.apps import apps as django_apps
from django.test import TestCase, tag
from django.test.utils import override_settings
from django.conf import settings

from ..import_holidays import import_holidays
from ..system_checks import holiday_check


class TestSystemChecks(TestCase):
    def test_(self):
        app_configs = django_apps.get_app_configs()
        holiday_check(app_configs=app_configs)

    @override_settings(HOLIDAY_FILE=None)
    def test_file(self):
        app_configs = django_apps.get_app_configs()
        errors = holiday_check(app_configs=app_configs)
        self.assertIn("edc_facility.001", [error.id for error in errors])

    @override_settings(
        HOLIDAY_FILE=os.path.join(
            settings.BASE_DIR, "edc_facility", "tests", "blah.csv"
        ),
        COUNTRY=None,
    )
    def test_bad_path(self):
        app_configs = django_apps.get_app_configs()
        errors = holiday_check(app_configs=app_configs)
        self.assertIn("edc_facility.002", [error.id for error in errors])

    @override_settings(
        HOLIDAY_FILE=os.path.join(
            settings.BASE_DIR, "edc_facility", "tests", "holidays.csv"
        ),
        COUNTRY=None,
    )
    def test_country(self):
        app_configs = django_apps.get_app_configs()
        errors = holiday_check(app_configs=app_configs)
        self.assertIn("edc_facility.003", [error.id for error in errors])

    @override_settings(
        HOLIDAY_FILE=os.path.join(
            settings.BASE_DIR, "edc_facility", "tests", "holidays.csv"
        ),
        COUNTRY="Netherlands",
    )
    def test_unknown_country(self):
        import_holidays()
        app_configs = django_apps.get_app_configs()
        errors = holiday_check(app_configs=app_configs)
        self.assertIn("edc_facility.004", [error.id for error in errors])
