from django.core import mail
from django.test import TestCase, tag
from edc_action_item.site_action_items import site_action_items
from edc_notification import NewModelNotification, UpdatedModelNotification
from edc_notification.site_notifications import site_notifications
from unittest.case import skip

from ..models import ActionItem
from .action_items import register_actions
from .models import SubjectIdentifierModel, FormZero


class TestActionNotification(TestCase):

    def setUp(self):
        register_actions()
        self.subject_identifier_model = ActionItem.subject_identifier_model
        ActionItem.subject_identifier_model = 'edc_action_item.subjectidentifiermodel'
        self.subject_identifier = '12345'
        SubjectIdentifierModel.objects.create(
            subject_identifier=self.subject_identifier)

    def tearDown(self):
        ActionItem.subject_identifier_model = self.subject_identifier_model

    @skip('notification')
    def test_notification_registration(self):
        """Asserts that by registering the action class, the
        notification class is also registered.

        (if action_cls.notifications_enabled = True)
        """
        action_enabled_for_notifications = []
        for action_cls in site_action_items.registry.values():
            if action_cls.notifications_enabled:
                action_enabled_for_notifications.append(action_cls)

        self.assertIsNotNone(action_enabled_for_notifications)

        # assert both the new and update are registered
        for action_cls in action_enabled_for_notifications:
            self.assertIn(
                action_cls.notification_name or action_cls.name,
                site_notifications.registry)
            self.assertIn(
                f'{action_cls.notification_name or action_cls.name}_update',
                site_notifications.registry)

        # assert class type for new and update
        for k, v in site_notifications.registry.items():
            if 'update' in k:
                self.assertTrue(issubclass(
                    v, UpdatedModelNotification), msg=v.name)
            else:
                self.assertTrue(issubclass(
                    v, NewModelNotification), msg=v.name)

    @tag('1')
    def test_action_sends_notification_on_new(self):
        FormZero.objects.create(
            subject_identifier=self.subject_identifier)
        self.assertEqual(len(mail.outbox), 1)
        self.assertNotIn('*UPDATE*', mail.outbox[0].subject)

    @tag('1')
    def test_action_sends_notification_does_not_duplicate_send(self):
        form_zero = FormZero.objects.create(
            subject_identifier=self.subject_identifier)
        self.assertEqual(len(mail.outbox), 1)
        form_zero.save()
        self.assertEqual(len(mail.outbox), 1)

    @tag('1')
    def test_action_sends_another_notification_on_update(self):
        form_zero = FormZero.objects.create(
            f1=1, subject_identifier=self.subject_identifier)
        self.assertEqual(len(mail.outbox), 1)
        form_zero.f1 = 2
        form_zero.save()
        self.assertEqual(len(mail.outbox), 2)
        form_zero.save()
        self.assertEqual(len(mail.outbox), 2)
        self.assertIn('*UPDATE*', mail.outbox[1].subject)

    @tag('2')
    def test_notification_updates_the_actions_model_as_emailed(self):
        form_zero = FormZero.objects.create(
            subject_identifier=self.subject_identifier)
        form_zero.refresh_from_db()
        self.assertTrue(form_zero.action_item.emailed)
        self.assertIsNotNone(form_zero.action_item.emailed_datetime)

    @tag('2')
    def test_action_sends_as_test_email(self):
        FormZero.objects.create(
            subject_identifier=self.subject_identifier)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('TEST/UAT', mail.outbox[0].subject)
        self.assertIn('THIS IS A TEST MESSAGE', mail.outbox[0].body)

    @tag('1')
    def test_action_sends_as_test_email_with_update(self):
        form_zero = FormZero.objects.create(
            f1=1, subject_identifier=self.subject_identifier)
        self.assertEqual(len(mail.outbox), 1)
        self.assertNotIn('*UPDATE*', mail.outbox[0].subject)
        self.assertIn('A report', mail.outbox[0].body)
        form_zero.f1 = 2
        form_zero.save()
        self.assertEqual(len(mail.outbox), 2)
        self.assertIn('*UPDATE*', mail.outbox[1].subject)
        self.assertIn('An updated report', mail.outbox[1].body)
