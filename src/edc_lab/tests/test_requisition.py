import re

from django.test import TestCase, tag

from ..identifiers import RequisitionIdentifier
from .models import SubjectRequisition


@tag('requisition')
class TestRequisition(TestCase):

    def test_requisition_identifier(self):
        """Asserts requisition identifier class creates identifier
        with correct format.
        """
        identifier = RequisitionIdentifier(SubjectRequisition)
        pattern = re.compile('[0-9]{2}[A-Z0-9]{5}')
        self.assertTrue(pattern.match(str(identifier)))
