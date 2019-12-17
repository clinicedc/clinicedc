from django.apps import apps as django_apps
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.test import TestCase, tag
from django.test.client import RequestFactory
from django.test.utils import override_settings

from ..backends import ModelBackendWithSite
from ..constants import CLINICIAN_ROLE
from ..models.role import Role
from ..group_permissions_updater import GroupPermissionsUpdater


class TestUserProfile(TestCase):
    #     def tearDown(self):
    #         UserProfile.objects.all().delete()
    #         User.objects.all().delete()

    def setUp(self):

        GroupPermissionsUpdater(verbose=True, apps=django_apps)

    def test_default_user_profile_created_by_signal(self):
        """Assert creates userprofile instance.
        """
        self.user = User.objects.create(username="noam")

    def test_backend_superuser(self):
        """Superuser can always log in.
        """
        user = User.objects.create(
            username="erik", is_superuser=True, is_active=True, is_staff=True
        )
        user.set_password("password")
        user.save()
        request = RequestFactory()
        backend = ModelBackendWithSite()
        self.assertIsNotNone(
            backend.authenticate(request, username="erik", password="password")
        )

    @override_settings(SITE_ID=10)
    def test_backend_one_site(self):
        """User of site 10 can login to site 10.
        """
        Site.objects.all().delete()
        ten = Site.objects.create(id=10, domain="ten.example.com", name="ten")
        user = User.objects.create(
            username="erik", is_superuser=False, is_active=True, is_staff=True
        )
        user.set_password("password")
        user.save()
        user.userprofile.sites.add(ten)
        request = RequestFactory()
        backend = ModelBackendWithSite()
        self.assertIsNotNone(
            backend.authenticate(request, username="erik", password="password")
        )

    @override_settings(SITE_ID=20)
    def test_backend_one_site2(self):
        """User of site 10 cannot login to site 20.
        """
        Site.objects.all().delete()
        ten = Site.objects.create(id=10, domain="ten.example.com", name="ten")
        user = User.objects.create(
            username="erik", is_superuser=False, is_active=True, is_staff=True
        )
        user.set_password("password")
        user.save()
        user.userprofile.sites.add(ten)
        request = RequestFactory()
        backend = ModelBackendWithSite()
        self.assertIsNone(
            backend.authenticate(request, username="erik", password="password")
        )

    @tag("2")
    def test_add_groups_for_role(self):
        user = User.objects.create(
            username="erik", is_superuser=False, is_active=True, is_staff=True
        )
        self.assertEqual(user.groups.all().count(), 0)
        role = Role.objects.get(name=CLINICIAN_ROLE)
        user.userprofile.roles.add(role)
        user.refresh_from_db()
        self.assertGreater(user.groups.all().count(), 0)
