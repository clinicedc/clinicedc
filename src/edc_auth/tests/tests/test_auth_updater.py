from copy import deepcopy
from importlib import import_module

from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, override_settings, tag

from edc_auth.auth_updater import AuthUpdater
from edc_auth.site_auths import site_auths
from edc_randomization.auth_objects import (
    RANDO_BLINDED,
    RANDO_UNBLINDED,
    get_rando_permissions_tuples,
)
from edc_randomization.randomizer import Randomizer
from edc_randomization.site_randomizers import site_randomizers

from ...auth_objects import default_groups
from ..randomizers import CustomRandomizer


@tag("auth")
@override_settings(
    EDC_AUTH_SKIP_SITE_AUTHS=False,
    EDC_AUTH_SKIP_AUTH_UPDATER=False,
)
class TestAuthUpdater(TestCase):
    @classmethod
    def setUpTestData(cls):
        site_randomizers._registry = {}
        site_randomizers.register(Randomizer)
        site_randomizers.register(CustomRandomizer)
        site_auths.initialize()
        import_module("edc_navbar.auths")
        import_module("edc_dashboard.auths")
        import_module("edc_review_dashboard.auths")
        import_module("edc_randomization.auths")

    def test_rando_tuples(self):
        """Given the two registered randomizers, assert view codenames are returned"""
        AuthUpdater(verbose=False, warn_only=True)
        self.assertIn(
            ("edc_randomization.view_randomizationlist", "Can view randomization list"),
            get_rando_permissions_tuples(),
        )

        self.assertIn(
            (
                "clinicedc_tests.view_customrandomizationlist",
                "Can view custom randomization list",
            ),
            get_rando_permissions_tuples(),
        )

    def test_removes_for_apps_not_installed_by_exact_match(self):
        """The app edc_action_blah is not installed, and will
        be removed."""
        groups = deepcopy(default_groups)
        groups.update(
            {
                "ACTION_GROUP": [
                    "edc_action_blah.view_actionitem",
                    "edc_action_item.view_actionitem",
                ]
            }
        )
        AuthUpdater(groups=groups, warn_only=True)
        groups = Group.objects.get(name="ACTION_GROUP")
        try:
            groups.permissions.get(
                content_type__app_label="edc_action_item", codename="view_actionitem"
            )
        except ObjectDoesNotExist:
            self.fail("Permission unexpectedly does not exist")

        self.assertRaises(
            ObjectDoesNotExist,
            groups.permissions.get,
            content_type__app_label="edc_action_blah",
            codename="view_actionitem",
        )

    def test_removes_edc_permissions_model_perms(self):
        qs = Permission.objects.filter(
            content_type__app_label="edc_auth",
            codename__in=[
                "add_edcpermissions",
                "change_edcpermissions",
                "view_edcpermissions",
                "delete_edcpermissions",
            ],
        )
        self.assertEqual(qs.count(), 4)
        AuthUpdater(verbose=False, warn_only=True)
        for group in Group.objects.all():
            qs = group.permissions.all()
            self.assertNotIn("add_dashboard", "|".join([o.codename for o in qs]))
            self.assertNotIn("change_dashboard", "|".join([o.codename for o in qs]))
            self.assertNotIn("view_dashboard", "|".join([o.codename for o in qs]))
            self.assertNotIn("delete_dashboard", "|".join([o.codename for o in qs]))

    def test_group_has_randomization_list_model_view_perms(self):
        """Assert group has view perms for each randomizer,
        others perms are removed.
        """
        AuthUpdater(verbose=False, warn_only=True)
        group = Group.objects.get(name=RANDO_BLINDED)
        qs = group.permissions.all()
        self.assertGreater(qs.count(), 0)
        self.assertIn("view_randomizationlist", "|".join([o.codename for o in qs]))
        group = Group.objects.get(name=RANDO_UNBLINDED)
        qs = group.permissions.all()
        self.assertGreater(qs.count(), 0)
        self.assertIn("view_randomizationlist", "|".join([o.codename for o in qs]))

    def test_randomization_list_model_add_change_delete_perms_removed_everywhere(self):
        AuthUpdater(verbose=False, warn_only=True)
        for group in Group.objects.all():
            qs = group.permissions.all()
            self.assertNotIn(
                "add_randomizationlist", "|".join([o.codename for o in qs])
            )
            self.assertNotIn(
                "change_randomizationlist", "|".join([o.codename for o in qs])
            )
            self.assertNotIn(
                "delete_randomizationlist", "|".join([o.codename for o in qs])
            )

    def test_removes_randomization_list_model_perms2(self):
        self.assertIn(
            "view_customrandomizationlist",
            "|".join([o.codename for o in Permission.objects.all()]),
        )
        AuthUpdater(verbose=False, warn_only=True)
        Permission.objects.filter(
            content_type__app_label__in=["edc_randomization", "tests"]
        )
        # confirm add_, change_, delete_ codenames for rando
        # does not exist in any groups.
        for group in Group.objects.all():
            qs = group.permissions.all()
            for model_name in ["customrandomizationlist", "randomizationlist"]:
                self.assertNotIn(
                    f"add_{model_name}", "|".join([o.codename for o in qs])
                )
                self.assertNotIn(
                    f"change_{model_name}", "|".join([o.codename for o in qs])
                )
                self.assertNotIn(
                    f"delete_{model_name}", "|".join([o.codename for o in qs])
                )
                if group.name in [RANDO_UNBLINDED, RANDO_BLINDED]:
                    self.assertIn(
                        f"view_{model_name}", "|".join([o.codename for o in qs])
                    )
