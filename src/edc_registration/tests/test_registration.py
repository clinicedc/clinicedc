from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.test.utils import override_settings, tag  # noqa
from edc_sites import add_or_update_django_sites
from edc_sites.tests import SiteTestCaseMixin
from edc_utils import get_utcnow
from multisite import SiteID

from ..models import RegisteredSubject, RegisteredSubjectError
from .models import SubjectModelOne, SubjectModelThree, SubjectModelTwo


class TestRegistration(SiteTestCaseMixin, TestCase):
    def test_creates_registered_subject(self):
        obj = SubjectModelOne.objects.create(screening_identifier="12345")
        try:
            RegisteredSubject.objects.get(
                registration_identifier=obj.to_string(obj.registration_identifier)
            )
        except ObjectDoesNotExist:
            self.fail("RegisteredSubject was unexpectedly not created")

    def test_updates_registered_subject(self):
        SubjectModelOne.objects.create(
            screening_identifier="12345", dob=get_utcnow() - relativedelta(years=5)
        )

        new_dob = get_utcnow().date()
        obj = SubjectModelOne.objects.get(screening_identifier="12345")
        obj.dob = new_dob
        obj.save()

        rs = RegisteredSubject.objects.get(
            registration_identifier=obj.to_string(obj.registration_identifier)
        )
        self.assertEqual(rs.dob, new_dob)

    def test_creates_registered_subject_overridden(self):
        """Assert creates RegisteredSubject with registration_unique_field overridden."""
        obj = SubjectModelTwo.objects.create(subject_identifier="12345")
        try:
            RegisteredSubject.objects.get(subject_identifier=obj.subject_identifier)
        except ObjectDoesNotExist:
            self.fail("RegisteredSubject was unexpectedly not created")

    def test_updates_registered_subject_overridden(self):
        """Assert updates RegisteredSubject with registration_unique_field overridden."""
        SubjectModelTwo.objects.create(
            subject_identifier="12345", dob=get_utcnow() - relativedelta(years=5)
        )

        new_dob = get_utcnow().date()
        obj = SubjectModelTwo.objects.get(subject_identifier="12345")
        obj.dob = new_dob
        obj.save()

        rs = RegisteredSubject.objects.get(subject_identifier=obj.subject_identifier)
        self.assertEqual(rs.dob, new_dob)

    def test_creates_registered_subject_overridden2(self):
        """Assert creates RegisteredSubject with registration_unique_field overridden."""
        obj = SubjectModelThree.objects.create(subject_identifier="12345")
        try:
            RegisteredSubject.objects.get(subject_identifier=obj.subject_identifier)
        except ObjectDoesNotExist:
            self.fail("RegisteredSubject was unexpectedly not created")

    def test_updates_registered_subject_overridden2(self):
        """Assert updates RegisteredSubject with registration_unique_field overridden."""
        SubjectModelThree.objects.create(
            subject_identifier="12345", dob=get_utcnow() - relativedelta(years=5)
        )

        new_dob = get_utcnow().date()
        obj = SubjectModelThree.objects.get(subject_identifier="12345")
        obj.dob = new_dob
        obj.save()

        rs = RegisteredSubject.objects.get(subject_identifier=obj.subject_identifier)
        self.assertEqual(rs.dob, new_dob)

    def test_subject_identifier_as_uuid(self):
        obj = SubjectModelOne.objects.create(screening_identifier="12345")
        rs = RegisteredSubject.objects.get(
            registration_identifier=obj.to_string(obj.registration_identifier)
        )
        self.assertFalse(rs.subject_identifier_is_set)

    def test_masks_if_not_set(self):
        obj = SubjectModelOne.objects.create(screening_identifier="12345")
        rs = RegisteredSubject.objects.get(
            registration_identifier=obj.to_string(obj.registration_identifier)
        )
        self.assertEqual(str(rs), "<identifier not set>")
        rs.subject_identifier = "ABCDEF"
        rs.save()
        rs = RegisteredSubject.objects.get(
            registration_identifier=obj.to_string(obj.registration_identifier)
        )
        self.assertEqual(str(rs), "ABCDEF")

    def test_cannot_change_subject_identifier(self):
        obj = SubjectModelOne.objects.create(screening_identifier="12345")
        rs = RegisteredSubject.objects.get(
            registration_identifier=obj.to_string(obj.registration_identifier)
        )
        rs.subject_identifier = "ABCDEF"
        rs.save()
        rs.subject_identifier = "WXYZ"
        self.assertRaises(RegisteredSubjectError, rs.save)

    @override_settings(SITE_ID=SiteID(10))
    def test_site1(self):
        add_or_update_django_sites(sites=self.default_sites, verbose=False)
        obj = SubjectModelOne.objects.create(screening_identifier="12345")
        rs = RegisteredSubject.objects.get(
            registration_identifier=obj.to_string(obj.registration_identifier)
        )
        self.assertEqual(rs.site.pk, 10)

    @override_settings(SITE_ID=SiteID(20))
    def test_site2(self):
        add_or_update_django_sites(sites=self.default_sites, verbose=False)
        obj = SubjectModelOne.objects.create(screening_identifier="12345")
        rs = RegisteredSubject.objects.get(
            registration_identifier=obj.to_string(obj.registration_identifier)
        )
        self.assertEqual(rs.site.pk, 20)
