from django.apps import apps as django_apps
from django.contrib.auth.models import Permission, Group
from django.test import TestCase
from edc_auth.group_names import RANDO
from edc_randomization import Randomizer
from edc_randomization.site_randomizers import site_randomizers

from ..group_permissions_updater import GroupPermissionsUpdater
from .randomizers import CustomRandomizer


class GroupPermissionUpdater(TestCase):
    def setUp(self):
        site_randomizers._registry = {}
        site_randomizers.register(Randomizer)
        site_randomizers.register(CustomRandomizer)

    @staticmethod
    def test_update():
        GroupPermissionsUpdater(apps=django_apps)

    def test_removes_for_apps_not_installed_by_exact_match(self):
        """The app edc_action_blah is not installed, and will
        be removed."""
        obj = GroupPermissionsUpdater(
            apps=django_apps,
            codenames_by_group={
                "ACTION_GROUP": [
                    "edc_action_blah.view_actionitem",
                    "edc_action_item.view_actionitem",
                ]
            },
        )

        self.assertNotIn(
            "edc_action_blah.view_mymodel", obj.codenames_by_group.get("ACTION_GROUP")
        )
        self.assertIn(
            "edc_action_item.view_actionitem",
            obj.codenames_by_group.get("ACTION_GROUP"),
        )

    def test_removes_edc_dashboard_dashboard_model_perms(self):
        GroupPermissionsUpdater()
        Permission.objects.filter(content_type__app_label="edc_dashboard")
        for group in Group.objects.all():
            qs = group.permissions.all()
            self.assertNotIn("add_dashboard", "|".join([o.codename for o in qs]))
            self.assertNotIn("change_dashboard", "|".join([o.codename for o in qs]))
            self.assertNotIn("view_dashboard", "|".join([o.codename for o in qs]))
            self.assertNotIn("delete_dashboard", "|".join([o.codename for o in qs]))

    def test_edc_dashboard_perms_before_update(self):
        qs = Permission.objects.filter(
            content_type__app_label="edc_dashboard"
        ).order_by("codename")
        self.assertEqual(
            "|".join([o.codename for o in qs]),
            "add_dashboard|change_dashboard|delete_dashboard|export_dashboard|"
            "import_dashboard|view_dashboard",
        )

    def test_removes_randomization_list_model_perms(self):
        GroupPermissionsUpdater()

        Permission.objects.filter(content_type__app_label="edc_randomization")
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

        group = Group.objects.get(name=RANDO)
        qs = group.permissions.all()
        self.assertIn("view_randomizationlist", "|".join([o.codename for o in qs]))

    def test_removes_randomization_list_model_perms2(self):
        self.assertIn(
            "view_customrandomizationlist",
            "|".join([o.codename for o in Permission.objects.all()]),
        )
        GroupPermissionsUpdater(verbose=True)
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
