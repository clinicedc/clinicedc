import re

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, tag
from edc_constants.constants import UUID_PATTERN
from edc_identifier.models import IdentifierModel

from .models import SubjectScreening


class TestScreening(TestCase):
    def test_model(self):

        obj = SubjectScreening.objects.create(age_in_years=25)

        try:
            IdentifierModel.objects.get(identifier=obj.screening_identifier)
        except ObjectDoesNotExist:
            self.fail(f"Identifier unexpectedly not found. {obj.screening_identifier}")

        self.assertTrue(re.match(UUID_PATTERN, obj.subject_identifier))
