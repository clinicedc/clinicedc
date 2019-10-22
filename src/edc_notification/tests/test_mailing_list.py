import requests

from django.contrib.auth.models import User
from django.test import TestCase, tag
from django.test.utils import override_settings
from unittest.mock import patch

from ..mailing_list_manager import EmailNotEnabledError
from ..mailing_list_manager import MailingListManager
from ..notification import GradedEventNotification
from ..site_notifications import site_notifications


class G3EventNotification(GradedEventNotification):
    name = "g3_event"
    display_name = "Test Grade3 Event"
    grade = 3
    model = "edc_notification.ae"
    email_to = ["somemailinglist@example.com"]


class TestMailingList(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="erikvw",
            is_active=True,
            is_staff=True,
            email="erikvw@example.com",
            first_name="erik",
            last_name="halfabee",
        )
        self.user.userprofile.job_title = "drummer"
        site_notifications._registry = {}
        site_notifications.register(G3EventNotification)
        self.notification_cls = site_notifications.get("g3_event")

    @override_settings(MAILGUN_API_KEY="123456", MAILGUN_API_URL="http://localhost")
    @patch("requests.post")
    @patch("requests.put")
    def test_(self, mock_put, mock_post):
        mail = MailingListManager()
        mail.enabled = True

        self.assertEqual("http://localhost", mail.api_url)

        self.assertEqual("123456", mail.api_key)

    @override_settings(MAILGUN_API_KEY=None, MAILGUN_API_URL=None)
    def test_api(self):
        mail = MailingListManager()
        mail.enabled = True

        self.assertRaises(EmailNotEnabledError, getattr, mail, "api_url")
        self.assertRaises(EmailNotEnabledError, getattr, mail, "api_key")

    @override_settings(MAILGUN_API_KEY="123456", MAILGUN_API_URL="mock://localhost")
    @patch("requests.post")
    def test_subscribe(self, mock_post):
        manager = MailingListManager(
            address=self.notification_cls.email_to[0],
            display_name=self.notification_cls.display_name,
            name=self.notification_cls.name,
        )
        manager.enabled = True
        manager.subscribe(self.user, True)
        self.assertIn(
            "mock://localhost/somemailinglist@example.com/members",
            str(requests.post.call_args_list),
        )
        self.assertIn("auth=('api', '123456')", str(requests.post.call_args_list))
        self.assertIn(
            "data={'subscribed': True, "
            "'address': 'erikvw@example.com', "
            "'name': 'erik halfabee', "
            "'description': 'drummer', "
            "'upsert': 'yes'}",
            str(requests.post.call_args_list),
        )

    @override_settings(MAILGUN_API_KEY="123456", MAILGUN_API_URL="mock://localhost")
    @patch("requests.put")
    def test_unsubscribe(self, mock_put):
        manager = MailingListManager(
            address=self.notification_cls.email_to[0],
            display_name=self.notification_cls.display_name,
            name=self.notification_cls.name,
        )
        manager.enabled = True
        manager.unsubscribe(self.user, True)
        self.assertIn(
            "mock://localhost/somemailinglist@example.com/members/erikvw@example.com",
            str(requests.put.call_args_list),
        )
        self.assertIn("auth=('api', '123456')", str(requests.put.call_args_list))
        self.assertIn("data={'subscribed': False}", str(requests.put.call_args_list))

    @override_settings(MAILGUN_API_KEY="123456", MAILGUN_API_URL="mock://localhost")
    @patch("requests.post")
    def test_create(self, mock_put):
        manager = MailingListManager(
            address=self.notification_cls.email_to[0],
            display_name=self.notification_cls.display_name,
            name=self.notification_cls.name,
        )
        manager.enabled = True
        manager.create(True)
        self.assertIn("mock://localhost", str(requests.post.call_args_list))
        self.assertIn("auth=('api', '123456')", str(requests.post.call_args_list))
        self.assertIn(
            "data={'address': 'somemailinglist@example.com', "
            "'name': 'g3_event', "
            "'description': 'Test Grade3 Event'}",
            str(requests.post.call_args_list),
        )

    @override_settings(MAILGUN_API_KEY="123456", MAILGUN_API_URL="mock://localhost")
    @patch("requests.delete")
    def test_delete_member(self, mock_delete):
        manager = MailingListManager(
            address=self.notification_cls.email_to[0],
            display_name=self.notification_cls.display_name,
            name=self.notification_cls.name,
        )
        manager.enabled = True
        manager.delete_member(self.user)
        self.assertIn(
            "mock://localhost/somemailinglist@example.com/members/erikvw@example.com",
            str(requests.delete.call_args_list),
        )
        self.assertIn("auth=('api', '123456')", str(requests.delete.call_args_list))

    @override_settings(MAILGUN_API_KEY="123456", MAILGUN_API_URL="mock://localhost")
    @patch("requests.delete")
    def test_delete(self, mock_delete):
        manager = MailingListManager(
            address=self.notification_cls.email_to[0],
            display_name=self.notification_cls.display_name,
            name=self.notification_cls.name,
        )
        manager.enabled = True
        manager.delete()
        self.assertIn(
            "mock://localhost/somemailinglist@example.com",
            str(requests.delete.call_args_list),
        )
        self.assertIn("auth=('api', '123456')", str(requests.delete.call_args_list))

    @override_settings(
        MAILGUN_API_KEY="123456",
        MAILGUN_API_URL="mock://localhost",
        EMAIL_ENABLED=True,
        EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend",
    )
    @patch("requests.post")
    @patch("requests.put")
    @patch("requests.delete")
    def test_create_mailing_lists(self, *args):
        responses = site_notifications.create_mailing_lists()
        self.assertIn("g3_event", responses)
