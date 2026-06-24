from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.test import TestCase, override_settings, tag
from django.test.client import RequestFactory

from edc_metadata.models import ReviewFilter
from edc_metadata.views.review_filter_views import (
    DeleteReviewFilterView,
    SaveReviewFilterView,
)


@tag("metadata")
@override_settings(SITE_ID=10)
class TestReviewFilter(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="erik")
        self.other = User.objects.create(username="jo")

    @staticmethod
    def _post(view_cls, data, user):
        request = RequestFactory().post("/", data=data)
        request.user = user
        request.session = {}
        request._messages = FallbackStorage(request)
        return view_cls().post(request)

    def test_unique_per_user_name(self):
        ReviewFilter.objects.create(user=self.user, name="A", query="site=")
        with transaction.atomic(), self.assertRaises(IntegrityError):
            ReviewFilter.objects.create(user=self.user, name="A", query="x=1")

    def test_save_view_creates_then_overwrites(self):
        self._post(
            SaveReviewFilterView, dict(name="mine", query="schedule=v%3A%3As"), self.user
        )
        obj = ReviewFilter.objects.get(user=self.user, name="mine")
        self.assertEqual(obj.query, "schedule=v%3A%3As")
        self.assertFalse(obj.shared)
        # re-saving the same name overwrites (update_or_create)
        self._post(
            SaveReviewFilterView, dict(name="mine", query="q=105", shared="1"), self.user
        )
        obj.refresh_from_db()
        self.assertEqual(obj.query, "q=105")
        self.assertTrue(obj.shared)
        self.assertEqual(ReviewFilter.objects.filter(user=self.user, name="mine").count(), 1)

    def test_visibility_is_own_plus_shared(self):
        mine = ReviewFilter.objects.create(user=self.user, name="mine", query="")
        shared = ReviewFilter.objects.create(
            user=self.other, name="team", query="", shared=True
        )
        ReviewFilter.objects.create(user=self.other, name="theirs", query="")  # hidden
        visible = ReviewFilter.objects.filter(Q(user=self.user) | Q(shared=True))
        self.assertEqual(set(visible), {mine, shared})

    def test_delete_owner_allowed_nonowner_denied(self):
        obj = ReviewFilter.objects.create(user=self.user, name="mine", query="")
        # a non-owner cannot delete someone else's personal filter
        self._post(DeleteReviewFilterView, dict(filter_id=str(obj.pk)), self.other)
        self.assertTrue(ReviewFilter.objects.filter(pk=obj.pk).exists())
        # the owner can
        self._post(DeleteReviewFilterView, dict(filter_id=str(obj.pk)), self.user)
        self.assertFalse(ReviewFilter.objects.filter(pk=obj.pk).exists())
