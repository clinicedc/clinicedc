from django.test import TestCase
from django.core.exceptions import ImproperlyConfigured
from django.contrib.contenttypes.models import ContentType

from edc.subject.lab_tracker.classes import LabTracker, site_lab_tracker
from edc.subject.lab_tracker.models import TestResultModel
from edc_configuration.models import GlobalConfiguration
from edc_content_type_map.models import ContentTypeMap
from edc_content_type_map.models import ContentTypeMapHelper
from edc_dashboard.exceptions import DashboardModelError
from edc_dashboard.subject import RegisteredSubjectDashboard
from edc_registration.tests.factories import RegisteredSubjectFactory
from edc_testing.models import TestVisit, TestConsentWithMixin, TestRequisition, TestSubjectLocator
from edc_testing.tests.factories import TestConsentWithMixinFactory
from edc_visit_schedule.tests.factories import VisitDefinitionFactory, ScheduleFactory, MembershipFormFactory


class DashboardTests(TestCase):

    def test_p2(self):
        print 'site_lab_tracker.autodiscover()'

        class TestLabTracker(LabTracker):
            subject_type = 'test_subject_type'
            trackers = [(TestResultModel, 'result', 'result_datetime', )]
            group_name = 'HIV'
            tracked_test_codes = ('HIV', 'ELISA', 'RELISA')
        site_lab_tracker.register(TestLabTracker)
        site_lab_tracker.autodiscover()
        content_type_map_helper = ContentTypeMapHelper()
        content_type_map_helper.populate()
        content_type_map_helper.sync()
        content_type = ContentType.objects.get(app_label='bhp_base_test', model='testconsentwithmixin')
        content_type_map = ContentTypeMap.objects.get(content_type=content_type)
        membership_form = MembershipFormFactory(content_type_map=content_type_map, category='subject')
        schedule = ScheduleFactory(membership_form=membership_form)
        visit_tracking_content_type_map = ContentTypeMap.objects.get(app_label='bhp_base_test', model='testvisit')
        visit_definition = VisitDefinitionFactory(visit_tracking_content_type_map=visit_tracking_content_type_map)
        visit_definition.schedule.add(schedule)
        registered_subject = RegisteredSubjectFactory(subject_type='test_subject_type')
        Configuration.objects.create()
        test_consent_with_mixin = TestConsentWithMixinFactory(registered_subject=registered_subject)
        self.assertRaises(TypeError, RegisteredSubjectDashboard,
            dashboard_type='subject',
            dashboard_id=test_consent_with_mixin.pk,
            dashboard_model=TestConsentWithMixin,
            dashboard_type_list=None,
            dashboard_models=None,
            visit_model=TestVisit
            )
        self.assertRaises(DashboardModelError, RegisteredSubjectDashboard,
            dashboard_type='subject',
            dashboard_id=test_consent_with_mixin.pk,
            dashboard_model=TestConsentWithMixin,
            dashboard_type_list=['subject'],
            dashboard_models=None,
            visit_model=TestVisit
            )
        print 'if null dashboard category raises ImproperlyConfigured exception'
        self.assertRaises(ImproperlyConfigured, RegisteredSubjectDashboard,
            dashboard_type='subject',
            dashboard_id=test_consent_with_mixin.pk,
            dashboard_model=TestConsentWithMixin,
            dashboard_type_list=['subject'],
            dashboard_models={'test_consent_with_mixin': TestConsentWithMixin},
            visit_model=TestVisit,
            registered_subject=registered_subject
            )
        print 'if invalid dashboard category raises ImproperlyConfigured exception'
        self.assertRaises(ImproperlyConfigured, RegisteredSubjectDashboard,
            dashboard_type='subject',
            dashboard_id=test_consent_with_mixin.pk,
            dashboard_model=TestConsentWithMixin,
            dashboard_category='my_category',
            dashboard_type_list=['subject'],
            dashboard_models={'test_consent_with_mixin': TestConsentWithMixin},
            visit_model=TestVisit,
            registered_subject=registered_subject
            )
        print 'can handle membership category as a string delimited by commas'
        membership_form.category = 'subject, subject, subject'
        membership_form.save()
        self.assertTrue(isinstance(RegisteredSubjectDashboard(
            dashboard_type='subject',
            dashboard_id=test_consent_with_mixin.pk,
            dashboard_model=TestConsentWithMixin,
            dashboard_category='subject',
            dashboard_type_list=['subject'],
            dashboard_models={'test_consent_with_mixin': TestConsentWithMixin},
            visit_model=TestVisit,
            registered_subject=registered_subject
            ), RegisteredSubjectDashboard))

        print 'if requisition not overriden, has_requisirtion_model returns False.'

        class TestDashboard1(RegisteredSubjectDashboard):
            dashboard_url_name = 'subject_dashboard_url'

            def get_visit_model(self):
                return TestVisit

        dashboard = TestDashboard1(
            dashboard_type='subject',
            dashboard_id=test_consent_with_mixin.pk,
            dashboard_model=TestConsentWithMixin,
            dashboard_category='subject',
            dashboard_type_list=['subject'],
            dashboard_models={'test_consent_with_mixin': TestConsentWithMixin},
            registered_subject=registered_subject
            )
        self.assertIsNone(dashboard.get_requisition_model())
        self.assertFalse(dashboard._get_has_requisition_model(), 'has_requisition_model not equal to False')

        print 'if get_visit_model method overridden, visit_model parameter not needed.'

        class TestDashboard2(RegisteredSubjectDashboard):
            dashboard_url_name = 'subject_dashboard_url'

            def get_visit_model(self):
                return TestVisit

            def get_requisition_model(self):
                return TestRequisition

        self.assertTrue(isinstance(TestDashboard2(
            dashboard_type='subject',
            dashboard_id=test_consent_with_mixin.pk,
            dashboard_model=TestConsentWithMixin,
            dashboard_category='subject',
            dashboard_type_list=['subject'],
            dashboard_models={'test_consent_with_mixin': TestConsentWithMixin},
            registered_subject=registered_subject
            ), TestDashboard2))

        dashboard = TestDashboard2(
            dashboard_type='subject',
            dashboard_id=test_consent_with_mixin.pk,
            dashboard_model=TestConsentWithMixin,
            dashboard_category='subject',
            dashboard_type_list=['subject'],
            dashboard_models={'test_consent_with_mixin': TestConsentWithMixin},
            registered_subject=registered_subject
            )
        print 'get_context'
        context = dashboard.get_context()
        self.assertEqual(dashboard.context.get().get('dashboard_type'), 'subject')
        self.assertEqual(dashboard.context.get().get('dashboard_id'), test_consent_with_mixin.pk)
        self.assertEqual(dashboard.context.get().get('dashboard_model'), 'test_consent_with_mixin')

        class TestDashboard3(RegisteredSubjectDashboard):
            dashboard_url_name = 'subject_dashboard_url'

            def get_visit_model(self):
                return TestVisit

            def get_requisition_model(self):
                return TestRequisition

            def get_locator_model(self):
                return TestSubjectLocator

        dashboard = TestDashboard3(
            dashboard_type='subject',
            dashboard_id=test_consent_with_mixin.pk,
            dashboard_model=TestConsentWithMixin,
            dashboard_category='subject',
            dashboard_type_list=['subject'],
            dashboard_models={'test_consent_with_mixin': TestConsentWithMixin},
            registered_subject=registered_subject
            )

        self.assertIsNotNone(dashboard.get_requisition_model())
        self.assertTrue(dashboard._get_has_requisition_model(), 'has_requisition_model not equal to True')

        print 'get_context (with locator)'
        context = dashboard.get_context()
        self.assertEqual(dashboard.context.get().get('dashboard_type'), 'subject')
        self.assertEqual(dashboard.context.get().get('dashboard_id'), test_consent_with_mixin.pk)
        self.assertEqual(dashboard.context.get().get('dashboard_model'), 'test_consent_with_mixin')
