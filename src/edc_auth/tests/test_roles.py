from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.test import tag
from faker import Faker

from ..models import Role
from ..role_names import CLINICIAN_ROLE, role_names, groups_by_role_name
from .utils import create_users, EdcAuthTestCase

fake = Faker()

site_names = ["harare", "gaborone", "kampala"]
user_model = get_user_model()


class TestRoles(EdcAuthTestCase):

    @tag("1")
    def test_post_migrate(self):
        """Assert post-migrate updated defaults for model Role."""
        self.assertGreater(Role.objects.all().count(), 0)
        for role_name in role_names:
            try:
                Role.objects.get(name=role_name)
            except ObjectDoesNotExist as e:
                self.fail(f"Role name unexpectedly does not exist. Got {e}")

    @tag("1")
    def test_add_roles_to_user(self):
        create_users()
        user = user_model.objects.all()[0]
        self.assertEqual(user.groups.all().count(), 0)
        role = Role.objects.get(name=CLINICIAN_ROLE)

        # should trigger post add m2m signal
        user.userprofile.roles.add(role)
        user.refresh_from_db()

        self.assertGreater(user.groups.all().count(), 0)
        role.refresh_from_db()
        groups = [group.name for group in role.groups.all()]
        groups.sort()

        self.assertEqual(groups, groups_by_role_name.get(CLINICIAN_ROLE))
