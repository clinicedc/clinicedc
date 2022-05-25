from importlib import import_module

from django.test import TestCase, override_settings
from edc_auth.auth_updater import AuthUpdater


class TestAuths(TestCase):
    @override_settings(
        EDC_AUTH_SKIP_SITE_AUTHS=True,
        EDC_AUTH_SKIP_AUTH_UPDATER=True,
    )
    def test_load(self):
        import_module("edc_dashboard.auths")
        import_module("edc_navbar.auths")
        AuthUpdater(verbose=True)
