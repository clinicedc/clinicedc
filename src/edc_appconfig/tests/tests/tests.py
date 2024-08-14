from django.apps import apps as django_apps
from django.test import TestCase, override_settings
from edc_action_item.system_checks import edc_action_item_checks
from edc_consent.system_checks import check_consents
from edc_export.system_checks import edc_export_checks
from edc_facility.system_checks import holiday_country_check, holiday_path_check
from edc_metadata.system_checks import check_for_metadata_rules
from edc_navbar.system_checks import edc_navbar_checks
from edc_sites.system_checks import sites_check
from edc_visit_schedule.system_checks import (
    check_form_collections,
    check_onschedule_exists_in_subject_schedule_history,
    check_subject_schedule_history,
    visit_schedule_check,
)


@override_settings(SILENCED_SYSTEM_CHECKS=[])
class TestAppConfig(TestCase):
    """These tests just run the checks even though the system is
    not configured, e.g. no consents, no sites, etc.
    """

    def test_sites(self):
        errors = sites_check(django_apps.get_app_configs())
        ids = [error.id for error in errors]
        self.assertEqual(2, len(ids))
        self.assertIn("edc_sites.E001", ids)
        self.assertIn("edc_sites.E002", ids)

    def test_check_site_consents(self):
        errors = check_consents(django_apps.get_app_configs())
        ids = [error.id for error in errors]
        self.assertEqual(0, len(ids))
        # self.assertIn("edc_consent.E001", ids)

    def test_edc_navbar_checks(self):
        errors = edc_navbar_checks(django_apps.get_app_configs())
        ids = [error.id for error in errors]
        self.assertEqual(9, len(ids))
        # self.assertIn("edc_navbar.E002", ids)
        self.assertIn("edc_navbar.E003", ids)

    def test_check_for_metadata_rules(self):
        errors = check_for_metadata_rules(django_apps.get_app_configs())
        ids = [error.id for error in errors]
        self.assertEqual(1, len(ids))
        self.assertIn("edc_metadata.W001", ids)

    def test_visit_schedule_check(self):
        errors = check_form_collections(django_apps.get_app_configs())
        ids = [error.id for error in errors]
        self.assertEqual(0, len(ids))

        errors = visit_schedule_check(django_apps.get_app_configs())
        ids = [error.id for error in errors]
        self.assertEqual(1, len(ids))
        self.assertIn("edc_visit_schedule.W001", ids)

        errors = check_onschedule_exists_in_subject_schedule_history(
            django_apps.get_app_configs()
        )
        ids = [error.id for error in errors]
        self.assertEqual(0, len(ids))

        errors = check_subject_schedule_history(django_apps.get_app_configs())
        ids = [error.id for error in errors]
        self.assertEqual(0, len(ids))

    def test_edc_export_checks(self):
        errors = edc_export_checks(django_apps.get_app_configs())
        ids = [error.id for error in errors]
        self.assertEqual(2, len(ids))
        self.assertIn("edc_export.W001", ids)
        self.assertIn("edc_export.W002", ids)

    def test_edc_facility_checks(self):
        errors = holiday_country_check(django_apps.get_app_configs())
        ids = [error.id for error in errors]
        self.assertEqual(0, len(ids))
        errors = holiday_path_check(django_apps.get_app_configs())
        ids = [error.id for error in errors]
        self.assertEqual(1, len(ids))
        self.assertIn("edc_facility.W001", ids)

    def test_edc_action_item_checks(self):
        warnings = edc_action_item_checks(django_apps.get_app_configs())
        ids = [warning.id for warning in warnings]
        self.assertEqual(0, len(ids))
