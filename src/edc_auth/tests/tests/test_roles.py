from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.test import override_settings
from faker import Faker

from edc_auth.auth_objects import (
    ACCOUNT_MANAGER_ROLE,
    AUDITOR_ROLE,
    CLINICIAN_ROLE,
    CLINICIAN_SUPER_ROLE,
    CUSTOM_ROLE,
    NURSE_ROLE,
    STAFF_ROLE,
)
from edc_auth.auth_objects.default_role_names import STATISTICIAN
from edc_auth.auth_updater import AuthUpdater
from edc_auth.models import Role
from edc_auth.site_auths import site_auths

from ..utils import EdcAuthTestCase, create_users

fake = Faker()

site_names = ["harare", "gaborone", "kampala"]
user_model = get_user_model()


@override_settings(
    EDC_AUTH_SKIP_SITE_AUTHS=False,
    EDC_AUTH_SKIP_AUTH_UPDATER=False,
)
class TestRoles(EdcAuthTestCase):
    def test_post_migrate(self):
        """Assert post-migrate updated defaults for model Role."""
        AuthUpdater(verbose=False)
        self.assertGreater(Role.objects.all().count(), 0)
        for role_name in [
            ACCOUNT_MANAGER_ROLE,
            AUDITOR_ROLE,
            CLINICIAN_ROLE,
            CLINICIAN_SUPER_ROLE,
            CUSTOM_ROLE,
            NURSE_ROLE,
            STAFF_ROLE,
            STATISTICIAN,
        ]:
            try:
                Role.objects.get(name=role_name)
            except ObjectDoesNotExist:
                self.fail(f"Role name unexpectedly does not exist. Got {role_name}")

        role = Role.objects.get(name=CLINICIAN_ROLE)
        groups_from_role = [group.name for group in role.groups.all()]
        groups_from_role.sort()
        groups_from_site_auths = site_auths.roles.get(CLINICIAN_ROLE)
        groups_from_site_auths.sort()
        self.assertEqual(groups_from_role, groups_from_site_auths)

    def test_add_roles_to_user(self):
        AuthUpdater(verbose=False)
        create_users()
        user = user_model.objects.all()[0]
        self.assertEqual(user.groups.all().count(), 0)
        role = Role.objects.get(name=CLINICIAN_ROLE)
        # should trigger post add m2m signal
        user.userprofile.roles.add(role)
        user.refresh_from_db()
        self.assertGreater(user.groups.all().count(), 0)
        # see groups_by_role_name for expected group counts
        # note, count is the unique list count
        self.assertEqual(user.groups.all().count(), len(site_auths.roles.get(CLINICIAN_ROLE)))

    def test_remove_roles_to_user(self):
        AuthUpdater(verbose=False)
        create_users()
        user = user_model.objects.all()[0]
        self.assertEqual(user.groups.all().count(), 0)
        clinician_role = Role.objects.get(name=CLINICIAN_ROLE)
        clinician_super_role = Role.objects.get(name=CLINICIAN_SUPER_ROLE)
        clinician_groups = site_auths.roles.get(CLINICIAN_ROLE)
        clinician_super_groups = site_auths.roles.get(CLINICIAN_SUPER_ROLE)
        unique_group_cnt = len(list(set(clinician_groups + clinician_super_groups)))
        user.userprofile.roles.add(clinician_role)
        user.userprofile.roles.add(clinician_super_role)
        user.refresh_from_db()
        self.assertEqual(user.groups.all().count(), unique_group_cnt)
        # should trigger post remove m2m signal
        user.userprofile.roles.remove(clinician_super_role)
        self.assertEqual(user.groups.all().count(), len(clinician_groups))
