from django.apps import apps as django_apps
from django.test import TestCase, tag

from ..enrollment_cap import EnrollmentCapReached
from .models import Enrollment
from edc_protocol.site_protocol_subjects import site_protocol_subjects
from edc_protocol.model_mixins import InvalidSubjectType

app_config = django_apps.get_app_config('edc_protocol')


class TestProtocol(TestCase):

    def test_repr_subject_types(self):
        self.assertGreater(len(site_protocol_subjects), 0)
        for subject_type in site_protocol_subjects:
            self.assertTrue(repr(subject_type))

    def test_str_subject_types(self):
        self.assertGreater(len(site_protocol_subjects), 0)
        for subject_type in site_protocol_subjects:
            self.assertTrue(str(subject_type))

    def test_registered(self):
        self.assertIn('edc_protocol.enrollment',
                      [obj.model for obj in site_protocol_subjects.registry.values()])
        self.assertIn('edc_protocol.enrollmentthree',
                      [obj.model for obj in site_protocol_subjects.registry.values()])

    def test_raises_on_enrollment_cap(self):
        for _ in range(0, 5):
            Enrollment.objects.create()
        self.assertRaises(
            EnrollmentCapReached,
            Enrollment.objects.create)

    def test_raises_on_enrollment_cap_not_found(self):
        self.assertRaises(
            InvalidSubjectType,
            Enrollment.objects.create,
            subject_type='mother')
