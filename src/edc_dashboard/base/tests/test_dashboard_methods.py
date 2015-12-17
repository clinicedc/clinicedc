from django.test import TestCase
from django.core.exceptions import ImproperlyConfigured

from edc.core.bhp_content_type_map.classes import ContentTypeMapHelper
from edc.subject.registration.models import RegisteredSubject
from edc.testing.models import TestConsent, TestVisit

from ..classes import Dashboard
from ..exceptions import DashboardModelError


class TestDashboardMethods(TestCase):

    def setUp(self):
        from edc.testing.tests.factories import TestConsentFactory
        content_type_map_helper = ContentTypeMapHelper()
        content_type_map_helper.populate()
        content_type_map_helper.sync()

        self.test_consent_factory = TestConsentFactory

    def test_p1(self):
        """test init"""
        test_consent = self.test_consent_factory()
        registered_subject = test_consent.registered_subject
        print registered_subject.first_name
        self.assertRaises(TypeError, Dashboard)
        self.assertRaises(TypeError, Dashboard, None, None, None)
        self.assertRaises(TypeError, Dashboard, 'subject', None, None)
        self.assertRaises(TypeError, Dashboard, 'subject', '--', None)
        self.assertRaises(TypeError, Dashboard, 'subject', '--', RegisteredSubject)
        self.assertRaises(TypeError, Dashboard, 'subject', registered_subject.pk, RegisteredSubject)

    def test_with_registered_subject(self):
        """assert OK if registered_subject is the dashboard model and is specified as model class"""
        test_consent = self.test_consent_factory()
        registered_subject = test_consent.registered_subject
        dashboard = Dashboard('subject', registered_subject.pk, RegisteredSubject, dashboard_type_list=['subject'])
        self.assertEquals(dashboard.dashboard_type, 'subject')
        self.assertEquals(dashboard.dashboard_models, {'registered_subject': RegisteredSubject})

    def test_dict_update(self):
        """assert correctly updates instead of adds to dictionary if added twice"""
        test_consent = self.test_consent_factory()
        registered_subject = test_consent.registered_subject
        dashboard = Dashboard('subject', registered_subject.pk, RegisteredSubject, dashboard_type_list=['subject'])
        dashboard.add_dashboard_model({'registered_subject': RegisteredSubject})
        self.assertEquals(dashboard.dashboard_model, RegisteredSubject)
        self.assertEquals(dashboard.dashboard_id, registered_subject.pk)
        self.assertEquals(dashboard.dashboard_model_name, 'registered_subject')

    def test_with_registered_subject2(self):
        """"assert OK if registered_subject is the dashboard model and is specified as a model_name instead of class"""
        test_consent = self.test_consent_factory()
        registered_subject = test_consent.registered_subject
        dashboard = Dashboard('subject', registered_subject.pk, 'registered_subject', dashboard_type_list=['subject'])
        self.assertEquals(dashboard.dashboard_type, 'subject')
        self.assertRaises(TypeError, dashboard.dashboard_model, RegisteredSubject)
        dashboard.add_dashboard_model({'registered_subject': RegisteredSubject})
        self.assertEquals(dashboard.dashboard_model, RegisteredSubject)
        self.assertEquals(dashboard.dashboard_id, registered_subject.pk)
        self.assertEquals(dashboard.dashboard_model_name, 'registered_subject')

    def test_param_list(self):
        """assert raises TypeErrors if incomplete parameter list"""
        test_consent = self.test_consent_factory()
        self.assertRaises(TypeError, Dashboard)
        self.assertRaises(TypeError, Dashboard, None, None, None)
        self.assertRaises(TypeError, Dashboard, 'subject', None, None)
        self.assertRaises(TypeError, Dashboard, 'subject', '--', None)
        self.assertRaises(TypeError, Dashboard, 'subject', '--', RegisteredSubject)
        self.assertRaises(TypeError, Dashboard, 'subject', test_consent.pk, TestConsent)

    def test_dashboard_model(self):
        """assert raises exception if dashboard model is not in dictionary"""
        test_consent = self.test_consent_factory()
        self.assertRaises(DashboardModelError, Dashboard, 'subject', test_consent.pk, TestConsent, dashboard_type_list=['subject'])

    def test_dashboard_model2(self):
        """assert OK if dashboard model is added to dictionary using the dashboard instance"""
        test_consent = self.test_consent_factory()
        registered_subject = test_consent.registered_subject
        dashboard = Dashboard('subject', registered_subject.pk, 'registered_subject', dashboard_type_list=['subject'])
        dashboard.add_dashboard_model({'test_consent': TestConsent})
        self.assertIn('test_consent', dashboard.dashboard_models)

    def test_dashboard_1(self):
        """assert OK if dashboard model is specified (and added) at init instead of on the dashboard instance"""
        test_consent = self.test_consent_factory()

        class D1(Dashboard):
            dashboard_url_name = 'subject_dashboard_url'

        dashboard = D1(
            'subject',
            test_consent.pk,
            TestConsent,
            dashboard_type_list=['subject'],
            dashboard_models={'test_consent': TestConsent})
        self.assertEquals(dashboard.dashboard_type, 'subject')
        self.assertRaises(TypeError, dashboard.dashboard_model, TestConsent)
        self.assertEquals(dashboard.dashboard_model, TestConsent)
        self.assertEquals(dashboard.dashboard_id, test_consent.pk)
        self.assertEquals(dashboard.dashboard_model_name, 'test_consent')

    def test_dashboard_2(self):
        """assert can add a model to the dashboard model list"""
        test_consent = self.test_consent_factory()
        dashboard = Dashboard(
            'subject',
            test_consent.pk,
            'test_consent',
            dashboard_type_list=['subject'],
            dashboard_models={'test_consent': TestConsent})
        self.assertIn('test_consent', dashboard.dashboard_models)
        self.assertEquals(dashboard.dashboard_type, 'subject')
        self.assertRaises(TypeError, dashboard.dashboard_model, TestConsent)
        dashboard.add_dashboard_model({'test_consent': TestConsent})
        self.assertEqual(sorted(['test_consent', 'registered_subject']), sorted(dashboard.dashboard_models))
        self.assertEquals(dashboard.dashboard_model, TestConsent)
        self.assertEquals(dashboard.dashboard_id, test_consent.pk)
        self.assertEquals(dashboard.dashboard_model_name, 'test_consent')
        self.assertTrue(isinstance(dashboard.dashboard_model_instance, TestConsent))

    def test_dashboard_3(self):
        """assert can convert a dashboard_model_list item from a function"""
        test_consent = self.test_consent_factory()

        class D1(Dashboard):
            dashboard_url_name = 'subject_dashboard_url'

        def get_visit_model():
            return TestVisit

        dashboard = D1(
            'subject',
            test_consent.pk,
            'test_consent',
            dashboard_type_list=['subject'],
            dashboard_models={'test_consent': TestConsent, 'test_visit': get_visit_model})
        self.assertIn('test_consent', dashboard.dashboard_models)
        self.assertEquals(dashboard.dashboard_type, 'subject')
        dashboard.add_dashboard_model({'test_consent': TestConsent})
        self.assertEqual(sorted(['test_consent', 'registered_subject', 'test_visit']), sorted(dashboard.dashboard_models))
        self.assertEquals(dashboard.dashboard_model, TestConsent)
        self.assertEquals(dashboard.dashboard_id, test_consent.pk)
        self.assertEquals(dashboard.dashboard_model_name, 'test_consent')
        self.assertTrue(isinstance(dashboard.dashboard_model_instance, TestConsent))

    def test_dashboard_4(self):
        """assert can convert a dashboard_model_list item from a method"""
        test_consent = self.test_consent_factory()

        class Obj(object):
            def get_visit_model(self):
                return TestVisit

        class D1(Dashboard):
            dashboard_url_name = 'subject_dashboard_url'

        dashboard = D1(
            'subject',
            test_consent.pk,
            'test_consent',
            dashboard_type_list=['subject'],
            dashboard_models={'test_consent': TestConsent, 'test_visit': Obj().get_visit_model})
        self.assertIn('test_consent', dashboard.dashboard_models)
        self.assertEquals(dashboard.dashboard_type, 'subject')
        dashboard.add_dashboard_model({'test_consent': TestConsent})
        self.assertEqual(sorted(['test_consent', 'registered_subject', 'test_visit']), sorted(dashboard.dashboard_models))
        self.assertEquals(dashboard.dashboard_model, TestConsent)
        self.assertEquals(dashboard.dashboard_id, test_consent.pk)
        self.assertEquals(dashboard.dashboard_model_name, 'test_consent')
        self.assertTrue(isinstance(dashboard.dashboard_model_instance, TestConsent))

    def test_dashboard_5(self):
        """assert method verify_dashboard_model"""
        test_consent = self.test_consent_factory()

        class D1(Dashboard):
            dashboard_url_name = 'subject_dashboard_url'

        class Obj(object):
            def get_visit_model(self):
                return TestVisit

        class Obj2(object):
            def get_visit_model(self):
                return TestVisit

        class D2(Dashboard):

            dashboard_url_name = 'subject_dashboard_url'

            def verify_dashboard_model(self, model):
                if model:
                    if not 'get_registered_subject_blah_blah' in dir(model):
                        raise ImproperlyConfigured('Dashboard model must have method get_registered_subject_blah_blah().')

        self.assertRaisesRegexp(ImproperlyConfigured, 'get_registered_subject_blah_blah', D2,
            'subject',
            test_consent.pk,
            'test_consent',
            dashboard_type_list=['subject'],
            dashboard_models={'test_consent': TestConsent, 'test_visit': Obj2().get_visit_model})

    def test_context(self):
        """get_context where models has a function"""
        test_consent = self.test_consent_factory()

        class Obj(object):
            def get_visit_model(self):
                return TestVisit

        class D1(Dashboard):
            dashboard_url_name = 'subject_dashboard_url'

        dashboard = D1(
            'subject',
            test_consent.pk,
            'test_consent',
            dashboard_type_list=['subject'],
            dashboard_models={'test_consent': TestConsent, 'test_visit': Obj().get_visit_model})

        dashboard.set_context()
        self.assertEqual(dashboard.context.get().get('dashboard_type'), 'subject')
        self.assertEqual(dashboard.context.get().get('dashboard_id'), test_consent.pk)
        self.assertEqual(dashboard.context.get().get('dashboard_model'), 'test_consent')
        self.assertEqual(dashboard.context.get().get('dashboard_model_instance'), test_consent)
        self.assertEqual(sorted(dashboard.context.get().keys()), sorted(['app_label', 'dashboard_id', 'dashboard_model', 'dashboard_model_instance', 'dashboard_type', 'dashboard_name', 'dashboard_url_name', 'hostname', 'template']))
