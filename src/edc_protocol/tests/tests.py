from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, tag

from edc_protocol import SubjectType, Cap

from ..enrollment_cap import EnrollmentCapReached
from .models import EnrollmentThree


class TestProtocol(TestCase):

    def setUp(self):
        app_config = django_apps.get_app_config('edc_protocol')
        app_config.subject_types = [
            SubjectType('subject', 'Research Subjects', Cap(
                model_name='edc_protocol.enrollmentthree', max_subjects=5))
        ]
        app_config.site_code = '10'
        app_config.site_name = 'test_site'
        app_config.ready()

    def test_raises_on_enrollment_cap_none(self):
        app_config = django_apps.get_app_config('edc_protocol')
        app_config.subject_types = [
            SubjectType('subject', 'Research Subjects', Cap(
                model_name='edc_protocol.enrollmentthree', max_subjects=1))
        ]
        app_config.site_code = '10'
        app_config.site_name = 'test_site'
        app_config.ready()
        EnrollmentThree.objects.create()
        self.assertRaises(
            EnrollmentCapReached,
            EnrollmentThree.objects.create)

    def test_raises_on_enrollment_cap_not_found(self):
        enrollment_model = EnrollmentThree()
        self.assertRaises(
            EnrollmentCapReached,
            enrollment_model.save)

    def test_raises_on_enrollment_cap_not_found2(self):
        app_config = django_apps.get_app_config('edc_protocol')
        app_config.enrollment_caps = {'myapp.erik': {'erik': 100}}
        enrollment_model = EnrollmentThree()
        self.assertRaises(
            EnrollmentCapReached,
            enrollment_model.save)

    def test_raises_on_enrollment_cap_invalid_subject_type(self):
        app_config = django_apps.get_app_config('edc_protocol')
        app_config.enrollment_caps = {
            'edc_edc_protocol.enrollmentmodel': {'erik': 100}}
        self.assertRaises(ImproperlyConfigured, app_config.ready)

    def test_raises_on_enrollment_cap_met(self):
        app_config = django_apps.get_app_config('edc_protocol')
        app_config.subject_types = {'maternal': 'Mothers'}
        app_config.enrollment_caps = {
            'edc_protocol.enrollmentmodel': {'maternal': 2}}
        EnrollmentThree.objects.create()
        EnrollmentThree.objects.create()
        enrollment_model = EnrollmentThree()
        self.assertRaises(
            EnrollmentCapReached,
            enrollment_model.save)
        self.assertEquals(EnrollmentThree.objects.all().count(), 2)
