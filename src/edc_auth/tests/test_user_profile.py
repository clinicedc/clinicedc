from django.test import TestCase, tag
from django.contrib.auth.models import User

from ..models import UserProfile


class TestUserProfile(TestCase):

    def tearDown(self):
        UserProfile.objects.all().delete()
        User.objects.all().delete()

    def test_default_user_profile_created_by_signal(self):
        """Assert creates userprofile instance.
        """
        self.user = User.objects.create(username='noam')
        self.assertIsNone(self.user.userprofile.country)
        self.assertIsNone(self.user.userprofile.study_country)
        self.assertIsNone(self.user.userprofile.study_site)
