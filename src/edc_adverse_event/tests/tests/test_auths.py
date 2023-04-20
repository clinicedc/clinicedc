from importlib import import_module

from django.test import TestCase, override_settings
from edc_auth.auth_updater import AuthUpdater
from edc_data_manager.auth_objects import DATA_MANAGER_ROLE, SITE_DATA_MANAGER_ROLE
from edc_export.auth_objects import EXPORT


class TestAuths(TestCase):
    @override_settings(
        EDC_AUTH_SKIP_SITE_AUTHS=True,
        EDC_AUTH_SKIP_AUTH_UPDATER=False,
    )
    def test_load(self):
        # import_module("edc_dashboard.auths")
        import_module("edc_navbar.auths")
        # import_module("edc_data_manager.auths")
        # import_module("edc_lab.auths")
        import_module("edc_adverse_event.auths")
        AuthUpdater.add_empty_groups_for_tests(EXPORT)
        AuthUpdater.add_empty_roles_for_tests(DATA_MANAGER_ROLE, SITE_DATA_MANAGER_ROLE)
        AuthUpdater(verbose=True)
