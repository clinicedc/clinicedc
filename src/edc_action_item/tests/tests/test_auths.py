from datetime import datetime
from importlib import import_module
from zoneinfo import ZoneInfo

import time_machine
from django.test import TestCase, override_settings, tag

from edc_auth.auth_updater import AuthUpdater
from edc_auth.constants import TMG_ROLE
from edc_auth.site_auths import site_auths
from edc_data_manager.auth_objects import DATA_MANAGER_ROLE, SITE_DATA_MANAGER_ROLE
from edc_export.constants import EXPORT

utc_tz = ZoneInfo("UTC")


@tag("action_item")
@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=utc_tz))
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
