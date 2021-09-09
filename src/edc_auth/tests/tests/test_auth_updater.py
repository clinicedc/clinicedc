from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, tag
from edc_randomization import Randomizer
from edc_randomization.auth_objects import get_rando_permissions_tuples
from edc_randomization.constants import RANDO
from edc_randomization.site_randomizers import site_randomizers

from edc_auth.auth_updater import AuthUpdater

from ..randomizers import CustomRandomizer


class TestAuthUpdater(TestCase):
    def setUp(self):
        site_randomizers._registry = {}
        site_randomizers.register(Randomizer)
        site_randomizers.register(CustomRandomizer)

    def test_rando_tuples(self):
        """Given the two registered randomizers, assert view codenames are returned"""
        self.assertIn(
            ("edc_randomization.view_randomizationlist", "Can view randomization list"),
            get_rando_permissions_tuples(),
        )

        self.assertIn(
            (
                "edc_auth.view_customrandomizationlist",
                "Can view custom randomization list",
            ),
            get_rando_permissions_tuples(),
        )

    @staticmethod
    def test_update():
        AuthUpdater()

    def test_removes_for_apps_not_installed_by_exact_match(self):
        """The app edc_action_blah is not installed, and will
        be removed."""
        AuthUpdater(
            groups={
                "ACTION_GROUP": [
                    "edc_action_blah.view_actionitem",
                    "edc_action_item.view_actionitem",
                ]
            },
        )
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

    def test_removes_edc_dashboard_dashboard_model_perms(self):
        AuthUpdater()
        Permission.objects.filter(content_type__app_label="edc_dashboard")
        for group in Group.objects.all():
            qs = group.permissions.all()
            self.assertNotIn("add_dashboard", "|".join([o.codename for o in qs]))
            self.assertNotIn("change_dashboard", "|".join([o.codename for o in qs]))
            self.assertNotIn("view_dashboard", "|".join([o.codename for o in qs]))
            self.assertNotIn("delete_dashboard", "|".join([o.codename for o in qs]))

    def test_edc_dashboard_perms_before_update(self):
        """Perms for the dummy model edc_dashboard"""
        qs = Permission.objects.filter(
            content_type__app_label="edc_dashboard"
        ).order_by("codename")
        for codename in [
            "add_dashboard",
            "change_dashboard",
            "delete_dashboard",
            "export_dashboard",
            "import_dashboard",
            "view_dashboard",
        ]:
            self.assertIn(codename, "|".join([o.codename for o in qs]))

    @tag("1")
    def test_group_has_randomization_list_model_view_perms(self):
        """Assert group has view perms for each randomizer,
        others perms are removed.
        """
        AuthUpdater()
        group = Group.objects.get(name=RANDO)
        qs = group.permissions.all()
        self.assertGreater(qs.count(), 0)
        self.assertIn("view_randomizationlist", "|".join([o.codename for o in qs]))

    def test_randomization_list_model_add_change_delete_perms_removed_everywhere(self):
        AuthUpdater()
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

    @tag("1")
    def test_removes_randomization_list_model_perms2(self):
        self.assertIn(
            "view_customrandomizationlist",
            "|".join([o.codename for o in Permission.objects.all()]),
        )
        AuthUpdater(verbose=True)
        Permission.objects.filter(
            content_type__app_label__in=["edc_randomization", "edc_auth"]
        )
        # confirm add_, change_, delete_ codenames for rando
        # do not exists in any groups.
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
                if group.name == RANDO:
                    self.assertIn(
                        f"view_{model_name}", "|".join([o.codename for o in qs])
                    )
