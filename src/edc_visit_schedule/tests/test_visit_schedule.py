from django.test import TestCase
from django.apps import apps as django_apps

from edc_appointment.mixins import AppointmentMixin
from edc_meta_data.models import CrfEntry, LabEntry

from edc_visit_schedule.visit_schedule_configuration import MembershipFormTuple, ScheduleTuple
from edc_visit_schedule.models import MembershipForm, Schedule, VisitDefinition
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from example.models import RegisteredSubject, SubjectConsent
from edc_constants.constants import MALE, YES
from django.utils import timezone
from edc_content_type_map.apps import edc_content_type_callback, EdcContentTypeAppConfig


class TestVisitSchedule(TestCase):

    def setUp(self):
        edc_content_type_callback(EdcContentTypeAppConfig)
        app_config = django_apps.get_app_config('edc_content_type_map')
        app_config.ready()
        subject_identifier = '123456789'
        self.registered_subject = RegisteredSubject.objects.create(subject_identifier=subject_identifier)
        self.subject_consent = SubjectConsent.objects.create(
            subject_identifier=subject_identifier,
            registered_subject=self.registered_subject,
            consent_datetime=timezone.now(),
            gender=MALE,
            identity='123156789',
            confirm_identity='123156789',
            is_literate=YES,
        )
        self.visit_schedule.build()

    @property
    def visit_schedule(self):
        return site_visit_schedules.get_visit_schedule('example')

    def test_build_membership_form(self):
        """Creates as many instances of membership_form as in the config."""
        self.assertEqual(MembershipForm.objects.all().count(), len(self.visit_schedule.membership_forms.values()))

    def test_build_schedule(self):
        """Creates as many instances of schedule as in the config."""
        self.assertEqual(Schedule.objects.count(), len(self.visit_schedule.schedules.values()))

    def test_build_visit_definition(self):
        """Creates as many instances of visit_definition as in the config."""
        self.assertEqual(VisitDefinition.objects.count(), len(self.visit_schedule.visit_definitions.values()))

    def test_build_entry(self):
        """Creates as many instances of entry as in the config."""
        for code in self.visit_schedule.visit_definitions:
            self.assertEqual(
                CrfEntry.objects.filter(visit_definition__code=code).count(),
                len(self.visit_schedule.visit_definitions[code].get('entries')))
        self.assertGreater(CrfEntry.objects.count(), 0)

    def test_build_lab_entry(self):
        """Creates as many instances of lab_entry as in the config."""
        for code in self.visit_schedule.visit_definitions:
            self.assertEqual(
                LabEntry.objects.filter(visit_definition__code=code).count(),
                len(self.visit_schedule.visit_definitions[code].get('requisitions')))
        self.assertGreater(LabEntry.objects.count(), 0)

    def test_visit_definition_knows_membership_form(self):
        """Visit definition knows the MembershipForm and the model is a subclass of AppointmentMixin"""
        for visit_definition_name in self.visit_schedule.visit_definitions:
            schedule_name = self.visit_schedule.visit_definitions.get(
                visit_definition_name).get('schedule')
            schedule = self.visit_schedule.schedules.get(schedule_name)
            # the membership_form named tuple in dictionary visit_schedule.membership_forms.
            self.assertTrue(
                issubclass(self.visit_schedule.membership_forms.get(
                    schedule.membership_form_name).__class__,
                    MembershipFormTuple))
            # the model in the membership_form named tuple.
            self.assertTrue(
                issubclass(self.visit_schedule.membership_forms.get(schedule.membership_form_name).model,
                           AppointmentMixin))

    def test_visit_definition_knows_schedule(self):
        """Visit definition knows Schedule and it is a subclass of the named tuple."""
        for visit_definition_name in self.visit_schedule.visit_definitions:
            schedule_name = self.visit_schedule.visit_definitions.get(visit_definition_name).get('schedule')
            self.assertTrue(issubclass(self.visit_schedule.schedules.get(schedule_name).__class__, ScheduleTuple))

#     def test_can_create_membership_form_model_instance(self):
#         """Can create and instance of the membership form model."""
#         for visit_definition_name in self.visit_schedule.visit_definitions:
#             schedule_name = self.visit_schedule.visit_definitions[visit_definition_name].get('schedule')
#             schedule = self.visit_schedule.schedules.get(schedule_name)
#             self.visit_schedule.membership_forms[schedule.membership_form_name].model
#             self.assertIsNotNone(
#                 TestConsentWithMixinFactory(
#                     registered_subject=RegisteredSubjectFactory(),
#                     gender='M',
#                     identity='123456789',
#                     confirm_identity='123456789',
#                     study_site='10'))
