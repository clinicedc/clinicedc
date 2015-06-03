from uuid import UUID

from django.db.utils import IntegrityError
from django.test import TestCase

from edc_identifier.exceptions import IdentifierError

from edc_sample.sample.models import RegisteredSubject


class TestRegisteredSubject(TestCase):

    def test_subject_identifier_not_none(self):
        """Asserts subject identifier cannot be None after save()."""
        rs = RegisteredSubject()
        self.assertTrue(isinstance(rs.subject_identifier_as_pk, UUID))
        self.assertTrue(not rs.subject_identifier)
        rs.save()
        self.assertEquals(rs.subject_identifier, str(rs.subject_identifier_as_pk))

    def test_subject_identifier_is_pk(self):
        """Asserts subject identifier is a uuid after save()."""
        rs = RegisteredSubject()
        self.assertTrue(isinstance(rs.subject_identifier_as_pk, UUID))
        rs.save()
        self.assertEquals(rs.subject_identifier, str(rs.subject_identifier_as_pk))

    def test_subject_identifier_as_pk_not_none(self):
        """Asserts subject identifier is a uuid after save()."""
        rs = RegisteredSubject()
        self.assertTrue(isinstance(rs.subject_identifier_as_pk, UUID))
        rs.subject_identifier_as_pk = None
        self.assertRaises(ValueError, rs.save)

    def test_subject_identifier_constraint(self):
        """Asserts cannot accept duplicate on as_pk."""
        rs = RegisteredSubject()
        rs.save()
        dup = rs.subject_identifier_as_pk
        rs = RegisteredSubject(subject_identifier_as_pk=dup)
        self.assertRaises(IntegrityError, rs.save)

    def test_duplicate_subject_identifier(self):
        subject_identifier = '123456789'
        rs = RegisteredSubject(subject_identifier=subject_identifier)
        rs.save()
        self.assertEquals(rs.subject_identifier, subject_identifier)
        rs = RegisteredSubject(subject_identifier=subject_identifier)
        self.assertRaises(IdentifierError, rs.save)
