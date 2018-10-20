from django.core import mail
from django.test import TestCase, tag
from edc_base.utils import get_utcnow

from ..contrib import GradedEventNotification, NewModelNotification, UpdatedModelNotification
from ..decorators import register
from ..notification import Notification
from ..site_notifications import site_notifications, AlreadyRegistered
from .models import AE, Death


class TestNotification(TestCase):

    def test_register(self):
        class G4EventNotification(GradedEventNotification):

            name = 'g4_event'
            display_name = 'a grade 4 event has occured'
            grade = 4
            models = ['ambition_prn.aeinitial', 'ambition_prn.aefollowup']

        site_notifications._registry = {}
        site_notifications.register(G4EventNotification)
        klass = site_notifications.get(G4EventNotification.name)
        self.assertEqual(klass, G4EventNotification)
        self.assertTrue(site_notifications.loaded)

    def test_register_by_decorator(self):
        site_notifications._registry = {}

        @register()
        class ErikNotification(Notification):
            name = 'erik'

        klass = site_notifications.get(ErikNotification.name)
        self.assertEqual(klass, ErikNotification)

        with self.assertRaises(AlreadyRegistered) as cm:
            @register()
            class Erik2Notification(Notification):
                name = 'erik'
        self.assertEqual(cm.exception.__class__, AlreadyRegistered)

    def test_graded_event_grade3(self):

        site_notifications._registry = {}

        @register()
        class G3EventNotification(GradedEventNotification):
            name = 'g3_event'
            grade = 3
            model = 'edc_notification.ae'

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

        @register()
        class G4EventNotification(GradedEventNotification):
            name = 'g4_event'
            grade = 4
            model = 'edc_notification.ae'

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

        @register()
        class DeathNotification(NewModelNotification):
            name = 'death'
            model = 'edc_notification.death'

        death = Death.objects.create(subject_identifier='1')
        self.assertEqual(len(mail.outbox), 1)
        death.save()
        self.assertEqual(len(mail.outbox), 1)

    @tag('1')
    def test_updated_model_notification(self):

        site_notifications._registry = {}

        @register()
        class DeathNotification(UpdatedModelNotification):
            name = 'death'
            model = 'edc_notification.death'

        death = Death.objects.create(subject_identifier='1')
        self.assertEqual(len(mail.outbox), 0)
        death.save()
        self.assertEqual(len(mail.outbox), 1)
        death.save()
        self.assertEqual(len(mail.outbox), 2)

    def test_updated_model_notification2(self):

        site_notifications._registry = {}

        @register()
        class DeathNotification(UpdatedModelNotification):
            name = 'death'
            model = 'edc_notification.death'
            fields = ['report_datetime']

        death = Death.objects.create(subject_identifier='1')
        self.assertEqual(len(mail.outbox), 0)
        death.save()
        self.assertEqual(len(mail.outbox), 0)
        death.report_datetime = get_utcnow()
        death.save()
        self.assertEqual(len(mail.outbox), 1)
        death.save()
        self.assertEqual(len(mail.outbox), 1)
        death.report_datetime = get_utcnow()
        death.save()
        self.assertEqual(len(mail.outbox), 2)
