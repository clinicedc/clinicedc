from tempfile import mkdtemp

from django.apps import apps as django_apps
from django.test import TestCase, override_settings

from edc_randomization.randomization_list_verifier import RandomizationListError
from edc_randomization.system_checks import (
    blinded_trial_settings_check,
    randomizationlist_check,
)

from ..testcase_mixin import TestCaseMixin


class TestRandomizer(TestCaseMixin, TestCase):
    def test_randomization_list_check(self):
        errors = randomizationlist_check(
            app_configs=django_apps.get_app_config("edc_randomization")
        )
        self.assertNotIn("1000", [e.id for e in errors])
        self.assertIn("1001", [e.id for e in errors])

    @override_settings(ETC_DIR=mkdtemp())
    def test_system_check_bad_etc_dir(self):
        self.assertRaises(
            RandomizationListError,
            randomizationlist_check,
            app_configs=django_apps.get_app_config("edc_randomization"),
            force_verify=True,
        )

    @override_settings(ETC_DIR=mkdtemp(), DEBUG=False)
    def test_randomization_list_check_verify(self):
        from django.conf import settings

        self.assertFalse(settings.DEBUG)
        errors = randomizationlist_check(
            app_configs=django_apps.get_app_config("edc_randomization")
        )
        self.assertIn("1000", [e.id for e in errors])
        self.assertIn("1001", [e.id for e in errors])

    @override_settings(
        EDC_RANDOMIZATION_BLINDED_TRIAL=False, EDC_RANDOMIZATION_UNBLINDED_USERS=["audrey"]
    )
    def test_blinded_trial_settings_check(self):
        errors = blinded_trial_settings_check(
            app_configs=django_apps.get_app_config("edc_randomization")
        )
        self.assertIn("edc_randomization.E002", [e.id for e in errors])

    @override_settings(
        EDC_RANDOMIZATION_BLINDED_TRIAL=True, EDC_RANDOMIZATION_UNBLINDED_USERS=["audrey"]
    )
    def test_blinded_trial_settings_check2(self):
        errors = blinded_trial_settings_check(
            app_configs=django_apps.get_app_config("edc_randomization")
        )
        self.assertNotIn("edc_randomization.E002", [e.id for e in errors])
