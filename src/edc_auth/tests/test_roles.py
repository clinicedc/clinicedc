from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.test import tag  # noqa
from faker import Faker

from ..constants import DATA_MANAGER_ROLE
from ..models import Role
from ..role_names import CLINICIAN_ROLE, role_names, groups_by_role_name
from .utils import create_users, EdcAuthTestCase

fake = Faker()

site_names = ["harare", "gaborone", "kampala"]
user_model = get_user_model()


class TestRoles(EdcAuthTestCase):
    def test_post_migrate(self):
        """Assert post-migrate updated defaults for model Role."""
        self.assertGreater(Role.objects.all().count(), 0)
        for role_name in role_names:
            try:
                Role.objects.get(name=role_name)
            except ObjectDoesNotExist as e:
                self.fail(f"Role name unexpectedly does not exist. Got {e}")

        role = Role.objects.get(name=CLINICIAN_ROLE)
        groups = [group.name for group in role.groups.all()]
        groups.sort()
        self.assertEqual(groups, groups_by_role_name.get(CLINICIAN_ROLE))

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
        self.assertEqual(user.groups.all().count(), 10)

    def test_remove_roles_to_user(self):
        create_users()
        user = user_model.objects.all()[0]
        self.assertEqual(user.groups.all().count(), 0)
        clinician_role = Role.objects.get(name=CLINICIAN_ROLE)
        data_manager_role = Role.objects.get(name=DATA_MANAGER_ROLE)

        user.userprofile.roles.add(clinician_role)
        user.userprofile.roles.add(data_manager_role)
        user.refresh_from_db()
        cnt = user.groups.all().count()
        # see groups_by_role_name for expected group counts
        self.assertEqual(cnt, 10 + 2)
        # should trigger post remove m2m signal
        user.userprofile.roles.remove(data_manager_role)
        self.assertGreater(cnt, user.groups.all().count())
