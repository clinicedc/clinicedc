from importlib import import_module

from django.test import TestCase, override_settings, tag
from edc_auth.auth_updater import AuthUpdater
from edc_auth.site_auths import site_auths


class TestAuths(TestCase):
    @override_settings(
        EDC_AUTH_SKIP_SITE_AUTHS=True,
        EDC_AUTH_SKIP_AUTH_UPDATER=False,
    )
    def test_load(self):
        site_auths.initialize()
        import_module("edc_randomization.auths")
        AuthUpdater(verbose=False)
        # site_auths.initialize()
        # import_module("edc_navbar.auths")
        # import_module("edc_dashboard.auths")
        # import_module("edc_review_dashboard.auths")
        # import_module("edc_randomization.auths")
