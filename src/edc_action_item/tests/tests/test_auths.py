from importlib import import_module

from django.test import TestCase, override_settings
from edc_adverse_event.auth_objects import TMG_ROLE
from edc_auth.auth_updater import AuthUpdater
from edc_auth.site_auths import site_auths
from edc_data_manager.auth_objects import DATA_MANAGER_ROLE, SITE_DATA_MANAGER_ROLE
from edc_export.auth_objects import EXPORT


class TestAuths(TestCase):
    @override_settings(
        EDC_AUTH_SKIP_SITE_AUTHS=True,
        EDC_AUTH_SKIP_AUTH_UPDATER=False,
    )
    def test_load(self):
        site_auths.initialize()
        AuthUpdater.add_empty_groups_for_tests(EXPORT)
        AuthUpdater.add_empty_roles_for_tests(
            TMG_ROLE, DATA_MANAGER_ROLE, SITE_DATA_MANAGER_ROLE
        )
        import_module("edc_action_item.auths")
        AuthUpdater(verbose=True)
