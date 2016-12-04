from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from edc_example.models import EnrollmentThree

from .exceptions import SubjectTypeCapError


class TestProtocol(TestCase):

    def test_raises_on_enrollment_cap_none(self):
        app_config = django_apps.get_app_config('edc_protocol')
        app_config.enrollment_caps = {}
        enrollment_model = EnrollmentThree()
        self.assertRaises(SubjectTypeCapError, enrollment_model.raise_on_cap_met, app_config=app_config)

    def test_raises_on_enrollment_cap_not_found(self):
        app_config = django_apps.get_app_config('edc_protocol')
        app_config.enrollment_caps = {'myapp.erik': {'erik': -1}}
        enrollment_model = EnrollmentThree()
        self.assertRaises(SubjectTypeCapError, enrollment_model.raise_on_cap_met, app_config=app_config)

    def test_raises_on_enrollment_cap_not_found2(self):
        app_config = django_apps.get_app_config('edc_protocol')
        app_config.enrollment_caps = {'myapp.erik': {'erik': 100}}
        enrollment_model = EnrollmentThree()
        self.assertRaises(SubjectTypeCapError, enrollment_model.raise_on_cap_met, app_config=app_config)

    def test_raises_on_enrollment_cap_invalid_subject_type(self):
        app_config = django_apps.get_app_config('edc_protocol')
        app_config.enrollment_caps = {'edc_example.enrollmentmodel': {'erik': 100}}
        self.assertRaises(ImproperlyConfigured, app_config.ready)

    def test_raises_on_enrollment_cap_met(self):
        app_config = django_apps.get_app_config('edc_protocol')
        app_config.subject_types = {'maternal': 'Mothers'}
        app_config.enrollment_caps = {'example.enrollmentmodel': {'maternal': 2}}
        EnrollmentThree.objects.create()
        EnrollmentThree.objects.create()
        enrollment_model = EnrollmentThree()
        self.assertRaises(SubjectTypeCapError, enrollment_model.raise_on_cap_met, app_config=app_config)
        self.assertEquals(EnrollmentThree.objects.all().count(), 2)
