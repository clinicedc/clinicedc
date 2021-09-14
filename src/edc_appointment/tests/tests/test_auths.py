from importlib import import_module

from django.test import TestCase, override_settings, tag
from edc_auth.auth_updater import AuthUpdater
from edc_data_manager.auth_objects import DATA_MANAGER_ROLE
from edc_export.auth_objects import EXPORT


class TestAuths(TestCase):
    @override_settings(
        EDC_AUTH_SKIP_SITE_AUTHS=True,
        EDC_AUTH_SKIP_AUTH_UPDATER=False,
    )
    def test_load(self):
        AuthUpdater.add_empty_groups_for_tests(EXPORT)
        AuthUpdater.add_empty_roles_for_tests(DATA_MANAGER_ROLE)
        import_module("edc_appointment.auths")
        AuthUpdater(verbose=True)
