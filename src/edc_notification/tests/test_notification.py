import sys

from datetime import timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.color import color_style
from django.test import TestCase, tag
from edc_base.utils import get_utcnow

from ..decorators import register
from ..notification import GradedEventNotification, NewModelNotification
from ..notification import Notification, UpdatedModelNotification
from ..site_notifications import site_notifications, AlreadyRegistered
from ..models import Notification as NotificationModel
from .models import AE, Death

style = color_style()


class TestNotification(TestCase):

    def test_register(self):
        class G4EventNotification(GradedEventNotification):

            name = 'g4_event'
            display_name = 'a grade 4 event has occured'
            grade = 4
            models = ['ambition_prn.aeinitial', 'ambition_prn.aefollowup']

        site_notifications._registry = {}
        site_notifications.register(G4EventNotification)
        site_notifications.update_notification_list()
        klass = site_notifications.get(G4EventNotification.name)
        self.assertEqual(klass, G4EventNotification)
        self.assertTrue(site_notifications.loaded)

    def test_register_by_decorator(self):
        site_notifications._registry = {}
        site_notifications.update_notification_list()

        @register()
        class ErikNotification(Notification):
            name = 'erik'
            display_name = 'Erik'

        site_notifications.update_notification_list()
        klass = site_notifications.get(ErikNotification.name)
        self.assertEqual(klass, ErikNotification)

        with self.assertRaises(AlreadyRegistered) as cm:
            @register()
            class Erik2Notification(Notification):
                name = 'erik'
                display_name = 'Erik'
        self.assertEqual(cm.exception.__class__, AlreadyRegistered)

    def test_graded_event_grade3(self):

        site_notifications._registry = {}
        site_notifications.update_notification_list()

        @register()
        class G3EventNotification(GradedEventNotification):
            name = 'g3_event'
            grade = 3
            model = 'edc_notification.ae'

        site_notifications.update_notification_list()

        # create new
        ae = AE.objects.create(subject_identifier='1', ae_grade=3)
        self.assertEqual(len(mail.outbox), 1)
        # re-save
        ae.save()
        self.assertEqual(len(mail.outbox), 1)
        # increase grade
        ae.ae_grade = 4
        ae.save()
        self.assertEqual(len(mail.outbox), 1)
        # decrease back to G3
        ae.ae_grade = 3
        ae.save()
        self.assertEqual(len(mail.outbox), 2)

    def test_graded_event_grade4(self):

        site_notifications._registry = {}
        site_notifications.update_notification_list()

        @register()
        class G4EventNotification(GradedEventNotification):
            name = 'g4_event'
            grade = 4
            model = 'edc_notification.ae'

        site_notifications.update_notification_list()

        # create new
        ae = AE.objects.create(subject_identifier='1', ae_grade=2)
        self.assertEqual(len(mail.outbox), 0)
        # increase grade
        ae.ae_grade = 2
        ae.save()
        self.assertEqual(len(mail.outbox), 0)
        # increase grade
        ae.ae_grade = 3
        ae.save()
        self.assertEqual(len(mail.outbox), 0)
        # increase grade
        ae.ae_grade = 4
        ae.save()
        self.assertEqual(len(mail.outbox), 1)
        # decrease back to G3
        ae.ae_grade = 3
        ae.save()
        self.assertEqual(len(mail.outbox), 1)

    @tag('1')
    def test_new_model_notification(self):

        site_notifications._registry = {}
        site_notifications.update_notification_list()

        @register()
        class DeathNotification(NewModelNotification):
            name = 'death'
            model = 'edc_notification.death'

        site_notifications.update_notification_list()
        death = Death.objects.create(subject_identifier='1')
        self.assertEqual(len(mail.outbox), 1)
        death.save()
        self.assertEqual(len(mail.outbox), 1)

    def test_updated_model_notification(self):

        site_notifications._registry = {}
        site_notifications.update_notification_list()

        @register()
        class DeathNotification(UpdatedModelNotification):
            name = 'death'
            model = 'edc_notification.death'
            fields = ['cause']

        site_notifications.update_notification_list()

        death = Death.objects.create(
            subject_identifier='1', cause='A')
        # this is an update notification, do nothing on create
        self.assertEqual(len(mail.outbox), 0)

        # update/change cause of death, notify
        death.cause = 'B'
        death.save()
        self.assertEqual(len(mail.outbox), 1)

        # re-save, do nothing
        death.save()
        self.assertEqual(len(mail.outbox), 1)

        # update/change cause of death, notify
        death.cause = 'A'
        death.save()
        self.assertEqual(len(mail.outbox), 2)

    def test_updated_model_notification2(self):

        site_notifications._registry = {}
        site_notifications.update_notification_list()

        @register()
        class DeathNotification(UpdatedModelNotification):
            name = 'death'
            model = 'edc_notification.death'
            fields = ['report_datetime']

        site_notifications.update_notification_list()

        death = Death.objects.create(
            subject_identifier='1', cause='A')
        self.assertEqual(len(mail.outbox), 0)
        death.save()
        self.assertEqual(len(mail.outbox), 0)

        death.report_datetime = get_utcnow() - timedelta(days=1)
        death.save()
        self.assertEqual(len(mail.outbox), 1)

        death.save()
        self.assertEqual(len(mail.outbox), 1)

        death.report_datetime = get_utcnow()
        death.save()
        self.assertEqual(len(mail.outbox), 2)

    def test_notification_model_is_updated(self):

        site_notifications._registry = {}
        site_notifications.update_notification_list()

        @register()
        class DeathNotification(UpdatedModelNotification):
            name = 'death'
            model = 'edc_notification.death'
            fields = ['report_datetime']

        site_notifications.update_notification_list()

        Death.objects.create(
            subject_identifier='1', cause='A')

        try:
            NotificationModel.objects.get(name=DeathNotification.name)
        except ObjectDoesNotExist:
            self.fail('NotificationModel unexpectedly does not exist')

        @register()
        class DeathNotification2(UpdatedModelNotification):
            name = 'death2'
            display_name = 'Death Two'
            model = 'edc_notification.death'
            fields = ['report_datetime']

        site_notifications.update_notification_list()

        Death.objects.create(
            subject_identifier='2', cause='A')

        try:
            NotificationModel.objects.get(name=DeathNotification2.name)
        except ObjectDoesNotExist:
            self.fail('NotificationModel unexpectedly does not exist')

    def test_notification_model_disables_unused(self):

        site_notifications._registry = {}
        site_notifications.update_notification_list()

        @register()
        class DeathNotification(UpdatedModelNotification):
            name = 'death'
            model = 'edc_notification.death'
            fields = ['report_datetime']

        @register()
        class DeathNotification2(UpdatedModelNotification):
            name = 'death2'
            display_name = 'Death Two'
            model = 'edc_notification.death'
            fields = ['report_datetime']

        site_notifications.update_notification_list()

        Death.objects.create(
            subject_identifier='1', cause='A')

        site_notifications._registry = {}
        site_notifications.update_notification_list()

        Death.objects.create(
            subject_identifier='1', cause='A')

        self.assertRaises(
            ObjectDoesNotExist,
            NotificationModel.objects.get,
            name=DeathNotification.name,
            enabled=True)

        self.assertRaises(
            ObjectDoesNotExist,
            NotificationModel.objects.get,
            name=DeathNotification2.name,
            enabled=True)

    def test_sms(self):

        if settings.ENVFILE != '.env':
            sys.stdout.write(style.NOTICE(
                'skipping test_sms. Credentials not in ENV\n'
                'See comment in settings file.\n'))
        else:
            user = User.objects.create(username='erikvw')
            user.userprofile.mobile = settings.TWILIO_TEST_RECIPIENT
            user.userprofile.save()

            site_notifications._registry = {}
            site_notifications.update_notification_list()

            @register()
            class DeathNotification(NewModelNotification):
                name = 'death'
                model = 'edc_notification.death'

            site_notifications.update_notification_list()

            user.userprofile.sms_notifications.add(
                NotificationModel.objects.get(name=DeathNotification.name))

            Death.objects.create(
                subject_identifier='1', cause='A',
                user_created='erikvw')
