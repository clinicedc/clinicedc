from django.apps import apps as django_apps
from django.test import TestCase, tag
from model_mommy import mommy

from edc_constants.constants import MALE
from edc_example.models import (
    Appointment, CrfOne, CrfTwo, CrfThree, CrfFive, CrfFour, Enrollment)
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from ..constants import REQUIRED, KEYED
from ..models import CrfMetadata, RequisitionMetadata

edc_registration_app_config = django_apps.get_app_config('edc_registration')


class MetadataRulesDisabledTests(TestCase):

    def setUp(self):
        self.app_config = django_apps.get_app_config('edc_metadata')
        edc_registration_app_config = django_apps.get_app_config(
            'edc_registration')
        RegisteredSubject = edc_registration_app_config.model
        subject_consent = mommy.make_recipe('edc_example.subjectconsent')
        self.registered_subject = RegisteredSubject.objects.get(
            subject_identifier=subject_consent.subject_identifier)
        enrollment = Enrollment.objects.create(
            subject_identifier=subject_consent.subject_identifier,
            schedule_name='schedule1')
        visit_schedule = site_visit_schedules.get_visit_schedule(
            enrollment._meta.visit_schedule_name)
        schedule = visit_schedule.get_schedule(enrollment._meta.label_lower)
        self.first_visit = schedule.get_first_visit()
        self.first_appointment = Appointment.objects.get(
            subject_identifier=enrollment.subject_identifier,
            visit_code=self.first_visit.code)
        self.panel_name = self.first_visit.requisitions[0].panel.name

    def test_visit_creates_metadata(self):
        """Assert still creates metadata if rules disabled.
        """
        self.subject_visit = mommy.make_recipe(
            'edc_example.subjectvisit',
            appointment=self.first_appointment,
            reason=SCHEDULED)
        self.assertEqual(
            CrfMetadata.objects.all().count(),
            len(self.first_visit.crfs))
        self.assertEqual(
            RequisitionMetadata.objects.all().count(),
            len(self.first_visit.requisitions))

    def test_updates_crf_metadata(self):
        """Asserts updated as KEYED even if rules disabled.
        """
        self.subject_visit = mommy.make_recipe(
            'edc_example.subjectvisit',
            appointment=self.first_appointment,
            reason=SCHEDULED)
        self.assertEqual(CrfMetadata.objects.all().count(),
                         len(self.first_visit.crfs))
        CrfOne.objects.create(subject_visit=self.subject_visit)
        self.assertEqual(CrfMetadata.objects.filter(
            entry_status=KEYED).count(), 1)

    def test_recreates_crf_metadata(self):
        """Asserts creates and updated as KEYED even if rules disabled.
        """
        self.subject_visit = mommy.make_recipe(
            'edc_example.subjectvisit',
            appointment=self.first_appointment,
            reason=SCHEDULED)
        self.assertEqual(CrfMetadata.objects.all().count(),
                         len(self.first_visit.crfs))
        CrfOne.objects.create(subject_visit=self.subject_visit)
        CrfMetadata.objects.filter(model='edc_example.crfone').delete()
        self.assertEqual(
            CrfMetadata.objects.filter(model='edc_example.crfone').count(), 0)
        self.subject_visit.save()
        self.assertGreater(
            CrfMetadata.objects.filter(model='edc_example.crfone').count(), 0)

    @tag('erik')
    def test_updates_crf_metadata_for_existing_with_rule(self):
        """Asserts creates and updates as KEYED even if rules disabled.
        """
        self.subject_visit = mommy.make_recipe(
            'edc_example.subjectvisit',
            appointment=self.first_appointment,
            reason=SCHEDULED)
        self.assertEqual(CrfMetadata.objects.all().count(),
                         len(self.first_visit.crfs))
        CrfFour.objects.create(subject_visit=self.subject_visit)
        CrfMetadata.objects.filter(model='edc_example.crffour').delete()
        self.subject_visit.save()
        self.assertGreater(
            CrfMetadata.objects.filter(model='edc_example.crffour').count(), 0)
        self.assertEqual(CrfMetadata.objects.filter(
            entry_status=KEYED).count(), 1)

    @tag('erik')
    def test_updates_crf_metadata_for_existing_without_rule(self):
        """Asserts creates and updates as KEYED even if rules disabled.
        """
        self.subject_visit = mommy.make_recipe(
            'edc_example.subjectvisit',
            appointment=self.first_appointment,
            reason=SCHEDULED)
        self.assertEqual(
            CrfMetadata.objects.all().count(), len(self.first_visit.crfs))
        CrfOne.objects.create(subject_visit=self.subject_visit)
        CrfMetadata.objects.filter(model='edc_example.crfone').delete()
        self.subject_visit.save()
        self.assertGreater(
            CrfMetadata.objects.filter(model='edc_example.crfone').count(), 0)
        self.assertEqual(CrfMetadata.objects.filter(
            entry_status=KEYED).count(), 1)


class MetadataRulesTests(TestCase):

    def setUp(self):
        django_apps.app_configs['edc_metadata'].metadata_rules_enabled = False
        visit_schedule = site_visit_schedules.get_visit_schedule(
            Enrollment._meta.visit_schedule_name)
        self.schedule = visit_schedule.get_schedule(
            Enrollment._meta.label_lower)
        self.first_visit = self.schedule.get_first_visit()
        self.panel_name = self.first_visit.requisitions[0].panel.name

    @tag('erik')
    def test_rules_disabled(self):
        """Asserts rules are disabled.

        Does not set entry status to NOT_REQUIRED for for female
        forms ('crftwo', 'crfthree').
        """
        subject_consent = mommy.make_recipe(
            'edc_example.subjectconsent',
            subject_identifier='123456789-0', gender=MALE)
        enrollment = mommy.make_recipe(
            'edc_example.enrollment',
            subject_identifier=subject_consent.subject_identifier,
            schedule_name='schedule1')
        appointment = Appointment.objects.get(
            subject_identifier=enrollment.subject_identifier,
            visit_code=self.first_visit.code)
        subject_visit = mommy.make_recipe(
            'edc_example.subjectvisit',
            appointment=appointment)
        self.assertEqual(
            CrfMetadata.objects.get(
                model=CrfTwo._meta.label_lower,
                subject_identifier=subject_visit.subject_identifier,
                visit_code=self.first_visit.code).entry_status, REQUIRED)
        self.assertEqual(
            CrfMetadata.objects.get(
                model=CrfThree._meta.label_lower,
                subject_identifier=subject_visit.subject_identifier,
                visit_code=self.first_visit.code).entry_status, REQUIRED)
        self.assertEqual(
            CrfMetadata.objects.get(
                model=CrfFour._meta.label_lower,
                subject_identifier=subject_visit.subject_identifier,
                visit_code=self.first_visit.code).entry_status, REQUIRED)
        self.assertEqual(
            CrfMetadata.objects.get(
                model=CrfFive._meta.label_lower,
                subject_identifier=subject_visit.subject_identifier,
                visit_code=self.first_visit.code).entry_status, REQUIRED)
