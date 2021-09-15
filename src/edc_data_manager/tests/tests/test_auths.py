from importlib import import_module

from django.test import TestCase, override_settings
from edc_auth.auth_updater import AuthUpdater
from edc_auth.site_auths import site_auths


@override_settings(
    EDC_AUTH_SKIP_SITE_AUTHS=False,
    EDC_AUTH_SKIP_AUTH_UPDATER=False,
)
class TestAuths(TestCase):
    def test_load(self):
        site_auths.initialize()
        import_module("edc_data_manager.auths")
        import_module("edc_dashboard.auths")
        import_module("edc_navbar.auths")
        AuthUpdater(verbose=False)
