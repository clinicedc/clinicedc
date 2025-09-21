from tempfile import mkdtemp

from django.apps import apps as django_apps
from django.test import TestCase, override_settings, tag
from multisite import SiteID

from edc_randomization.randomization_list_verifier import RandomizationListError
from edc_randomization.randomizer import Randomizer
from edc_randomization.site_randomizers import site_randomizers
from edc_randomization.system_checks import (
    blinded_trial_settings_check,
    randomizationlist_check,
)
from edc_sites.site import sites as site_sites

from ..utils import populate_randomization_list_for_tests

tmpdir1 = mkdtemp()
tmpdir2 = mkdtemp()


class MyRandomizer(Randomizer):
    name = "my_randomizer"
    model = "edc_randomization.myrandomizationlist"
    randomizationlist_folder = tmpdir1


@tag("randomization")
@override_settings(
    EDC_RANDOMIZATION_REGISTER_DEFAULT_RANDOMIZER=False,
    SITE_ID=SiteID(40),
)
class TestRandomizer(TestCase):
    def setUp(self):
        site_randomizers._registry = {}
        site_randomizers.register(MyRandomizer)

    @staticmethod
    def populate_list(randomizer_name=None, per_site=None, overwrite_site=None):
        site_names = [s.name for s in site_sites._registry.values()]
        populate_randomization_list_for_tests(
            randomizer_name=randomizer_name,
            site_names=site_names,
            per_site=per_site,
            overwrite_site=overwrite_site,
        )

    @override_settings(ETC_DIR=tmpdir1)
    def test_randomization_list_check1(self):
        self.populate_list(randomizer_name="my_randomizer", overwrite_site=True)
        errors = randomizationlist_check(
            app_configs=django_apps.get_app_config("edc_randomization"),
            force_verify=False,
        )
        # insecure config, not in etc
        self.assertNotIn("1000", [e.id for e in errors])
        # insecure config, writeable
        self.assertIn("1001", [e.id for e in errors])
        self.assertEqual(1, len(errors))

    # @override_settings(ETC_DIR=tmpdir1)
    def test_randomization_list_check2(self):
        self.populate_list(randomizer_name="my_randomizer", overwrite_site=True)
        errors = randomizationlist_check(
            app_configs=django_apps.get_app_config("edc_randomization"),
            force_verify=False,
        )
        # insecure config, not in etc
        self.assertIn("1000", [e.id for e in errors])
        self.assertIn("1001", [e.id for e in errors])
        self.assertEqual(2, len(errors))

    @override_settings(ETC_DIR=tmpdir2)
    def test_system_check_bad_etc_dir(self):
        class MyRandomizer1(Randomizer):
            name = "my_randomizer"
            model = "edc_randomization.myrandomizationlist"
            randomizationlist_folder = mkdtemp()

        site_randomizers._registry = {}
        site_randomizers.register(MyRandomizer1)
        self.assertRaises(
            RandomizationListError,
            randomizationlist_check,
            app_configs=django_apps.get_app_config("edc_randomization"),
            force_verify=True,
        )

    @override_settings(ETC_DIR=tmpdir2, DEBUG=False)
    def test_randomization_list_check_verify(self):
        from django.conf import settings

        self.assertFalse(settings.DEBUG)

        class MyRandomizer1(Randomizer):
            name = "my_randomizer"
            model = "edc_randomization.myrandomizationlist"
            randomizationlist_folder = tmpdir1

        site_randomizers._registry = {}
        site_randomizers.register(MyRandomizer1)

        errors = randomizationlist_check(
            app_configs=django_apps.get_app_config("edc_randomization")
        )
        # insecure config, not in etc
        self.assertIn("1000", [e.id for e in errors])
        # insecure config, writeable
        self.assertIn("1001", [e.id for e in errors])

    @override_settings(
        EDC_RANDOMIZATION_BLINDED_TRIAL=False,
        EDC_RANDOMIZATION_UNBLINDED_USERS=["audrey"],
    )
    def test_blinded_trial_settings_check(self):
        errors = blinded_trial_settings_check(
            app_configs=django_apps.get_app_config("edc_randomization")
        )
        self.assertIn("edc_randomization.E002", [e.id for e in errors])

    @override_settings(
        EDC_RANDOMIZATION_BLINDED_TRIAL=True,
        EDC_RANDOMIZATION_UNBLINDED_USERS=["audrey"],
    )
    def test_blinded_trial_settings_check2(self):
        errors = blinded_trial_settings_check(
            app_configs=django_apps.get_app_config("edc_randomization")
        )
        self.assertNotIn("edc_randomization.E002", [e.id for e in errors])
