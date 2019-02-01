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
from ..notification import ModelNotification
from ..notification import GradedEventNotification, NewModelNotification
from ..notification import Notification, UpdatedModelNotification
from ..site_notifications import site_notifications, AlreadyRegistered
from ..site_notifications import RegistryNotLoaded, NotificationNotRegistered
from ..models import Notification as NotificationModel
from .models import AE, Death

style = color_style()


class TestNotification(TestCase):
    def test_register(self):
        class G4EventNotification(GradedEventNotification):

            name = "g4_event"
            display_name = "a grade 4 event has occured"
            grade = 4
            models = ["ambition_prn.aeinitial", "ambition_prn.aefollowup"]

        site_notifications.autodiscover(verbose=True)
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
            name = "erik"
            display_name = "Erik"

        site_notifications.update_notification_list()
        klass = site_notifications.get(ErikNotification.name)
        self.assertEqual(klass, ErikNotification)

        with self.assertRaises(AlreadyRegistered) as cm:

            @register()
            class Erik2Notification(Notification):
                name = "erik"
                display_name = "Erik"

        self.assertEqual(cm.exception.__class__, AlreadyRegistered)

    def test_site_notifications(self):

        site_notifications._registry = {}
        site_notifications.loaded = False
        # registry
        self.assertRaises(RegistryNotLoaded, getattr, site_notifications, "registry")

        # repr
        class ErikNotification(Notification):
            name = "erik"
            display_name = "Erik"

        site_notifications.register(notification_cls=ErikNotification)
        self.assertTrue(repr(site_notifications))

        # get
        self.assertRaises(NotificationNotRegistered, site_notifications.get, "frisco")

    def test_duplicate_notifications(self):
        """Assert raises for non-unique names and non-unique display_names.
        """

        class ErikNotification1(Notification):
            name = "erik"
            display_name = "Erik"

        class ErikNotification2(Notification):
            name = "bob"
            display_name = "Erik"

        site_notifications._registry = {}
        site_notifications.register(notification_cls=ErikNotification1)
        self.assertRaises(
            AlreadyRegistered,
            site_notifications.register,
            notification_cls=ErikNotification2,
        )
        site_notifications.update_notification_list()

    def test_get_notification_cls(self):
        site_notifications._registry = {}

        site_notifications.loaded = False

        self.assertRaises(RegistryNotLoaded, site_notifications.get, "erik")

        site_notifications.update_notification_list()

        class ErikNotification(Notification):
            name = "erik"
            display_name = "Erik"

        site_notifications.register(notification_cls=ErikNotification)

        self.assertEqual(site_notifications.get("erik"), ErikNotification)

    def test_notification_model(self):
        """Assert repr and str.
        """
        site_notifications._registry = {}

        class ErikNotification(Notification):
            name = "erik"
            display_name = "Erik"

        site_notifications.register(notification_cls=ErikNotification)
        site_notifications.update_notification_list()
        notification = NotificationModel.objects.get(name="erik")
        self.assertTrue(str(notification))

    def test_notification(self):
        """Assert repr and str.
        """
        site_notifications._registry = {}

        class SomeNotification(Notification):
            name = "erik"
            display_name = "Erik"

        self.assertTrue(repr(SomeNotification()))
        self.assertTrue(str(SomeNotification()))

    def test_default_notification(self):

        site_notifications._registry = {}

        @register()
        class SomeNotification(Notification):
            name = "erik"
            display_name = "Erik"

        SomeNotification().notify(subject_identifier="12345", site_name="Gaborone")
        self.assertEqual(len(mail.outbox), 1)

        SomeNotification().send_test_email("someone@example.com")

        self.assertEqual(len(mail.outbox), 2)

    def test_graded_event_grade3(self):

        site_notifications._registry = {}
        site_notifications.update_notification_list()

        @register()
        class G3EventNotification(GradedEventNotification):
            name = "g3_event"
            grade = 3
            model = "edc_notification.ae"

        site_notifications.update_notification_list()

        # create new
        ae = AE.objects.create(subject_identifier="1", ae_grade=3)
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
            name = "g4_event"
            grade = 4
            model = "edc_notification.ae"

        site_notifications.update_notification_list()

        # create new
        ae = AE.objects.create(subject_identifier="1", ae_grade=2)
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

    def test_model_notification(self):
        class DeathNotification(ModelNotification):
            name = "death"
            model = "edc_notification.death"

        repr(DeathNotification())
        str(DeathNotification())

    def test_new_model_notification(self):

        site_notifications._registry = {}
        site_notifications.update_notification_list()

        @register()
        class DeathNotification(NewModelNotification):
            name = "death"
            model = "edc_notification.death"

        site_notifications.update_notification_list()
        death = Death.objects.create(subject_identifier="1")
        self.assertEqual(len(mail.outbox), 1)
        death.save()
        self.assertEqual(len(mail.outbox), 1)

    def test_updated_model_notification(self):

        site_notifications._registry = {}
        site_notifications.update_notification_list()

        @register()
        class DeathNotification(UpdatedModelNotification):
            name = "death"
            model = "edc_notification.death"
            fields = ["cause"]

        site_notifications.update_notification_list()

        death = Death.objects.create(subject_identifier="1", cause="A")
        # this is an update notification, do nothing on create
        self.assertEqual(len(mail.outbox), 0)

        # update/change cause of death, notify
        death.cause = "B"
        death.save()
        self.assertEqual(len(mail.outbox), 1)

        # re-save, do nothing
        death.save()
        self.assertEqual(len(mail.outbox), 1)

        # update/change cause of death, notify
        death.cause = "A"
        death.save()
        self.assertEqual(len(mail.outbox), 2)

    def test_updated_model_notification2(self):

        site_notifications._registry = {}
        site_notifications.update_notification_list()

        @register()
        class DeathNotification(UpdatedModelNotification):
            name = "death"
            model = "edc_notification.death"
            fields = ["report_datetime"]

        site_notifications.update_notification_list()

        death = Death.objects.create(subject_identifier="1", cause="A")
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
            name = "death"
            model = "edc_notification.death"
            fields = ["report_datetime"]

        site_notifications.update_notification_list()

        Death.objects.create(subject_identifier="1", cause="A")

        try:
            NotificationModel.objects.get(name=DeathNotification.name)
        except ObjectDoesNotExist:
            self.fail("NotificationModel unexpectedly does not exist")

        @register()
        class DeathNotification2(UpdatedModelNotification):
            name = "death2"
            display_name = "Death Two"
            model = "edc_notification.death"
            fields = ["report_datetime"]

        site_notifications.update_notification_list()

        Death.objects.create(subject_identifier="2", cause="A")

        try:
            NotificationModel.objects.get(name=DeathNotification2.name)
        except ObjectDoesNotExist:
            self.fail("NotificationModel unexpectedly does not exist")

    def test_notification_model_is_updated_message_content(self):

        site_notifications._registry = {}

        @register()
        class DeathNotification(NewModelNotification):
            name = "death"
            model = "edc_notification.death"

        @register()
        class DeathUpdateNotification(UpdatedModelNotification):
            name = "death_update"
            display_name = "Death (Updated Report)"
            model = "edc_notification.death"
            fields = ["cause"]

        site_notifications.update_notification_list()

        death = Death.objects.create(subject_identifier="1", cause="A")
        self.assertEqual(len(mail.outbox), 1)
        death.cause = "B"
        death.save()
        self.assertEqual(len(mail.outbox), 2)
        self.assertIn("*UPDATE*", mail.outbox[1].__dict__.get("subject"))

    def test_notification_model_disables_unused(self):

        site_notifications._registry = {}
        site_notifications.update_notification_list()

        @register()
        class DeathNotification(UpdatedModelNotification):
            name = "death"
            model = "edc_notification.death"
            fields = ["report_datetime"]

        @register()
        class DeathNotification2(UpdatedModelNotification):
            name = "death2"
            display_name = "Death Two"
            model = "edc_notification.death"
            fields = ["report_datetime"]

        site_notifications.update_notification_list()

        Death.objects.create(subject_identifier="1", cause="A")

        site_notifications._registry = {}
        site_notifications.update_notification_list()

        Death.objects.create(subject_identifier="1", cause="A")

        self.assertRaises(
            ObjectDoesNotExist,
            NotificationModel.objects.get,
            name=DeathNotification.name,
            enabled=True,
        )

        self.assertRaises(
            ObjectDoesNotExist,
            NotificationModel.objects.get,
            name=DeathNotification2.name,
            enabled=True,
        )

    def test_sms(self):

        if settings.ENVFILE != ".env":
            sys.stdout.write(
                style.NOTICE(
                    "skipping test_sms. Credentials not in ENV\n"
                    "See comment in settings file.\n"
                )
            )
        else:
            user = User.objects.create(username="erikvw")
            user.userprofile.mobile = settings.TWILIO_TEST_RECIPIENT
            user.userprofile.save()

            site_notifications._registry = {}
            site_notifications.update_notification_list()

            @register()
            class DeathNotification(NewModelNotification):
                name = "death"
                model = "edc_notification.death"

            site_notifications.update_notification_list()

            user.userprofile.sms_notifications.add(
                NotificationModel.objects.get(name=DeathNotification.name)
            )

            Death.objects.create(
                subject_identifier="1", cause="A", user_created="erikvw"
            )

    def test_graded_event_grade3_as_test_email_message(self):

        site_notifications._registry = {}
        site_notifications.update_notification_list()

        @register()
        class G3EventNotification(GradedEventNotification):
            name = "g3_event"
            grade = 3
            model = "edc_notification.ae"

        site_notifications.update_notification_list()

        G3EventNotification().send_test_email("someone@example.com")

    def test_graded_event_grade3_as_test_sms_message(self):

        site_notifications._registry = {}
        site_notifications.update_notification_list()

        @register()
        class G3EventNotification(GradedEventNotification):
            name = "g3_event"
            display_name = "Test Grade3 Event"
            grade = 3
            model = "edc_notification.ae"

        site_notifications.update_notification_list()

        G3EventNotification().send_test_sms(
            sms_recipient=settings.TWILIO_TEST_RECIPIENT
        )

    def test_graded_event_grade3_as_test_sms_message_to_subscribed_user(self):

        user = User.objects.create(username="erikvw", is_active=True, is_staff=True)

        site_notifications._registry = {}
        site_notifications.update_notification_list()

        @register()
        class G3EventNotification(GradedEventNotification):
            name = "g3_event"
            display_name = "Test Grade3 Event"
            grade = 3
            model = "edc_notification.ae"

        site_notifications.update_notification_list()
        notification = NotificationModel.objects.get(name=G3EventNotification.name)
        user.userprofile.sms_notifications.add(notification)
        user.userprofile.mobile = settings.TWILIO_TEST_RECIPIENT
        user.userprofile.save()

        self.assertIn(
            settings.TWILIO_TEST_RECIPIENT, G3EventNotification().sms_recipients
        )

        AE.objects.create(subject_identifier="1", ae_grade=3)

    def test_notification_model_instance_deletes_for_unregistered(self):

        User.objects.create(username="erikvw", is_active=True, is_staff=True)

        site_notifications._registry = {}
        site_notifications.update_notification_list(verbose=True)

        class G3EventNotification(GradedEventNotification):
            name = "g3_event"
            display_name = "Test Grade3 Event"
            grade = 3
            model = "edc_notification.ae"

        site_notifications.register(notification_cls=G3EventNotification)
        site_notifications.update_notification_list(verbose=True)

        self.assertEqual(site_notifications.get("g3_event"), G3EventNotification)

        try:
            NotificationModel.objects.get(name=G3EventNotification.name)
        except ObjectDoesNotExist as e:
            self.fail(
                f"Notification model instance unexpectedly does not exist. Got {e}"
            )

        site_notifications._registry = {}
        site_notifications.update_notification_list()

        self.assertRaises(
            ObjectDoesNotExist,
            NotificationModel.objects.get,
            name=G3EventNotification.name,
        )
