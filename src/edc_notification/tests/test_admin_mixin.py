from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import RequestFactory
from edc_model_admin import ModelAdminFormInstructionsMixin
from edc_notification import NotificationModelAdminMixin
from unittest.mock import patch

from ..notification import GradedEventNotification
from ..site_notifications import site_notifications
from .models import AE


class Mixin(NotificationModelAdminMixin, ModelAdminFormInstructionsMixin):

    model = AE


class G3EventNotification(GradedEventNotification):
    name = "g3_event"
    display_name = "Test Grade3 Event"
    grade = 3
    model = "edc_notification.ae"


class TestAdminMixin(TestCase):
    def setUp(self):

        self.user = User.objects.create(
            username="erikvw", is_active=True, is_staff=True
        )
        site_notifications._registry = {}
        site_notifications.register(G3EventNotification)
        self.notification_cls = site_notifications.get("g3_event")
        self.notification_model = self.notification_cls().notification_model

    @patch(
        "edc_notification.mailing_list_manager.MailingListManager.create",
        return_value=200,
    )
    @patch(
        "edc_notification.mailing_list_manager.MailingListManager.subscribe",
        return_value=200,
    )
    @patch(
        "edc_notification.mailing_list_manager.MailingListManager.unsubscribe",
        return_value=200,
    )
    def test_notification_instructions(
        self, mock_create, mock_subscribe, mock_unsubscribe
    ):

        rf = RequestFactory()
        request = rf.get("/")
        request.user = self.user
        mixin = Mixin()

        result = mixin.get_notification_instructions(request=request)
        self.assertIn(self.notification_cls.display_name, str(result))
        self.assertIn("1 notification", str(result))
        self.assertIn("subscribed to 0", str(result))

        self.user.userprofile.email_notifications.add(self.notification_model)

        result = mixin.get_notification_instructions(request=request)
        self.assertIn(self.notification_cls.display_name, str(result))
        self.assertIn("1 notification", str(result))
        self.assertIn("subscribed to 1", str(result))

    @patch(
        "edc_notification.mailing_list_manager.MailingListManager.create",
        return_value=200,
    )
    @patch(
        "edc_notification.mailing_list_manager.MailingListManager.subscribe",
        return_value=200,
    )
    @patch(
        "edc_notification.mailing_list_manager.MailingListManager.unsubscribe",
        return_value=200,
    )
    def test_add_change_instructions(
        self, mock_create, mock_subscribe, mock_unsubscribe
    ):

        rf = RequestFactory()
        request = rf.get("/")
        request.user = self.user
        mixin = Mixin()

        self.user.userprofile.email_notifications.add(self.notification_model)

        result = mixin.get_add_instructions({}, request=request)
        self.assertIn(self.notification_cls.display_name, str(result))
        self.assertIn("1 notification", str(result))
        self.assertIn("subscribed to 1", str(result))

        result = mixin.get_change_instructions({}, request=request)
        self.assertIn(self.notification_cls.display_name, str(result))
        self.assertIn("1 notification", str(result))
        self.assertIn("subscribed to 1", str(result))
