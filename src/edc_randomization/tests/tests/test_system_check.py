from tempfile import mkdtemp

from django.apps import apps as django_apps
from django.test import TestCase, override_settings, tag

from edc_randomization import RandomizationListError
from edc_randomization.system_checks import randomizationlist_check
from edc_randomization.tests.tests.testcase_mixin import TestCaseMixin


class TestRandomizer(TestCaseMixin, TestCase):
    @tag("4")
    def test_randomization_list_check(self):
        errors = randomizationlist_check(
            app_configs=django_apps.get_app_config("edc_randomization")
        )
        self.assertNotIn("1000", [e.id for e in errors])
        self.assertIn("1001", [e.id for e in errors])

    @tag("4")
    @override_settings(ETC_DIR=mkdtemp())
    def test_system_check_bad_etc_dir(self):
        self.assertRaises(
            RandomizationListError,
            randomizationlist_check,
            app_configs=django_apps.get_app_config("edc_randomization"),
            force_verify=True,
        )

    @tag("4")
    @override_settings(ETC_DIR=mkdtemp(), DEBUG=False)
    def test_randomization_list_check_verify(self):
        from django.conf import settings

        self.assertFalse(settings.DEBUG)
        errors = randomizationlist_check(
            app_configs=django_apps.get_app_config("edc_randomization")
        )
        self.assertIn("1000", [e.id for e in errors])
        self.assertIn("1001", [e.id for e in errors])
