from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.test import tag  # noqa
from edc_data_manager.auth_objects import (
    DATA_MANAGER_ROLE,
    data_manager_role_group_names,
)
from faker import Faker

from edc_auth.default_role_names import CLINICIAN_ROLE, default_role_names
from edc_auth.site_auths import site_auths

from ...models import Role
from ..utils import EdcAuthTestCase, create_users

fake = Faker()

site_names = ["harare", "gaborone", "kampala"]
user_model = get_user_model()


class TestRoles(EdcAuthTestCase):
    def test_post_migrate(self):
        """Assert post-migrate updated defaults for model Role."""
        self.assertGreater(Role.objects.all().count(), 0)
        for role_name in default_role_names:
            try:
                Role.objects.get(name=role_name)
            except ObjectDoesNotExist as e:
                self.fail(f"Role name unexpectedly does not exist. Got {e}")

        role = Role.objects.get(name=CLINICIAN_ROLE)
        groups_from_role = [group.name for group in role.groups.all()]
        groups_from_role.sort()
        groups_from_site_auths = site_auths.roles.get(CLINICIAN_ROLE)
        groups_from_site_auths.sort()
        self.assertEqual(groups_from_role, groups_from_site_auths)

    def test_add_roles_to_user(self):
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
        self.assertEqual(
            user.groups.all().count(), len(site_auths.roles.get(CLINICIAN_ROLE))
        )

    def test_remove_roles_to_user(self):
        create_users()
        user = user_model.objects.all()[0]
        self.assertEqual(user.groups.all().count(), 0)
        clinician_role = Role.objects.get(name=CLINICIAN_ROLE)
        data_manager_role = Role.objects.get(name=DATA_MANAGER_ROLE)
        clinician_groups = site_auths.roles.get(CLINICIAN_ROLE)
        unique_group_cnt = len(
            list(set(clinician_groups + data_manager_role_group_names))
        )
        user.userprofile.roles.add(clinician_role)
        user.userprofile.roles.add(data_manager_role)
        user.refresh_from_db()
        self.assertEqual(user.groups.all().count(), unique_group_cnt)
        # should trigger post remove m2m signal
        user.userprofile.roles.remove(data_manager_role)
        self.assertEqual(user.groups.all().count(), len(clinician_groups))
