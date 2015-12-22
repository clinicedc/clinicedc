from django.test import TestCase

from edc.core.bhp_content_type_map.classes import ContentTypeMapHelper
from edc.core.bhp_content_type_map.models import ContentTypeMap
from edc.core.bhp_variables.tests.factories import StudySpecificFactory, StudySiteFactory
from edc_appointment.models import Appointment
from edc.entry_meta_data.models import ScheduledEntryMetaData
from edc.subject.entry.tests.factories import EntryFactory, LabEntryFactory
from edc.subject.lab_tracker.classes import site_lab_tracker
from edc.subject.registration.models import RegisteredSubject
from edc.subject.visit_schedule.tests.factories import MembershipFormFactory, ScheduleGroupFactory, VisitDefinitionFactory
from edc.testing.tests.factories import TestConsentWithMixinFactory, TestScheduledModel1Factory

from edc_dashboard.subject import ScheduledEntryContext


class ScheduledEntryContextTests(TestCase):

    app_label = 'testing'
    consent_catalogue_name = 'v1'

    def setUp(self):
        from edc.testing.tests.factories import TestVisitFactory
        self.test_visit_factory = TestVisitFactory
        site_lab_tracker.autodiscover()
        StudySpecificFactory()
        StudySiteFactory()
        content_type_map_helper = ContentTypeMapHelper()
        content_type_map_helper.populate()
        content_type_map_helper.sync()
        content_type_map = ContentTypeMap.objects.get(content_type__model='TestConsentWithMixin'.lower())
        membership_form = MembershipFormFactory(content_type_map=content_type_map, category='subject')
        schedule_group = ScheduleGroupFactory(membership_form=membership_form, group_name='GROUP_NAME', grouping_key='GROUPING_KEY')
        visit_tracking_content_type_map = ContentTypeMap.objects.get(content_type__model='testvisit')
        self.visit_definition = VisitDefinitionFactory(code='T0', title='T0', grouping='subject', visit_tracking_content_type_map=visit_tracking_content_type_map)
        self.visit_definition.schedule_group.add(schedule_group)

        # add entries
        content_type_map = ContentTypeMap.objects.get(app_label='testing', model='testscheduledmodel1')
        EntryFactory(content_type_map=content_type_map, visit_definition=self.visit_definition, entry_order=100, entry_category='clinic', app_label='testing', model_name='testscheduledmodel1')
        content_type_map = ContentTypeMap.objects.get(app_label='testing', model='testscheduledmodel2')
        EntryFactory(content_type_map=content_type_map, visit_definition=self.visit_definition, entry_order=110, entry_category='clinic', app_label='testing', model_name='testscheduledmodel2')
        content_type_map = ContentTypeMap.objects.get(app_label='testing', model='testscheduledmodel3')
        EntryFactory(content_type_map=content_type_map, visit_definition=self.visit_definition, entry_order=120, entry_category='clinic', app_label='testing', model_name='testscheduledmodel3')

        # add requisitions
        LabEntryFactory(visit_definition=self.visit_definition, entry_order=100)
        LabEntryFactory(visit_definition=self.visit_definition, entry_order=110)
        LabEntryFactory(visit_definition=self.visit_definition, entry_order=120)

        self.test_consent = TestConsentWithMixinFactory(gender='M')

        self.registered_subject = RegisteredSubject.objects.get(subject_identifier=self.test_consent.subject_identifier)
        self.appointment = Appointment.objects.get(registered_subject=self.registered_subject)

    def test_url1(self):
        """Instance exists, model_url should be a change url, not add."""
        self.test_visit = self.test_visit_factory(appointment=self.appointment)
        TestScheduledModel1Factory(test_visit=self.test_visit)
        meta_data_instance = ScheduledEntryMetaData.objects.get(entry_status='KEYED', registered_subject=self.registered_subject, entry__app_label='testing', entry__model_name='testscheduledmodel1')
        scheduled_entry_context = ScheduledEntryContext(meta_data_instance, self.appointment, self.test_visit.__class__)
        self.assertNotIn('add', scheduled_entry_context.get_context().get('model_url'))

    def test_url2(self):
        """Instance does not exist, model_url should be an add url."""
        self.test_visit = self.test_visit_factory(appointment=self.appointment)
        meta_data_instance = ScheduledEntryMetaData.objects.get(registered_subject=self.registered_subject, entry__app_label='testing', entry__model_name='testscheduledmodel1')
        scheduled_entry_context = ScheduledEntryContext(meta_data_instance, self.appointment, self.test_visit.__class__)
        self.assertIn('add', scheduled_entry_context.get_context().get('model_url'))
