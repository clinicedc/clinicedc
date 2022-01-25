import re

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from edc_constants.constants import UUID_PATTERN
from edc_identifier.models import IdentifierModel

from .models import SubjectScreening, SubjectScreeningWithEligibilitySimple


class TestScreening(TestCase):
    def test_model(self):
        for model_cls in [SubjectScreening, SubjectScreeningWithEligibilitySimple]:
            with self.subTest(model_cls=model_cls):
                obj = model_cls.objects.create(age_in_years=25)

                try:
                    IdentifierModel.objects.get(identifier=obj.screening_identifier)
                except ObjectDoesNotExist:
                    self.fail(f"Identifier unexpectedly not found. {obj.screening_identifier}")

                self.assertTrue(re.match(UUID_PATTERN, obj.subject_identifier))

                screening_identifier = obj.screening_identifier
                obj.save()
                obj.refresh_from_db()
                self.assertEqual(screening_identifier, obj.screening_identifier)
