import re

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, override_settings
from edc_constants.constants import MALE, NO, UUID_PATTERN, YES
from edc_identifier.models import IdentifierModel

from edc_screening.age_evaluator import AgeEvaluator
from edc_screening.constants import ELIGIBLE, NOT_ELIGIBLE
from edc_screening.gender_evaluator import GenderEvaluator
from edc_screening.utils import (
    eligibility_display_label,
    format_reasons_ineligible,
    get_subject_screening_app_label,
    get_subject_screening_model,
    get_subject_screening_model_cls,
)

from .models import (
    SubjectScreening,
    SubjectScreeningWithEligibility,
    SubjectScreeningWithEligibilitySimple,
)


class TestScreening(TestCase):
    @override_settings(SUBJECT_SCREENING_MODEL="edc_screening.subjectscreening")
    def test_model_funcs(self):
        self.assertEqual(get_subject_screening_model(), "edc_screening.subjectscreening")
        self.assertEqual(get_subject_screening_app_label(), "edc_screening")
        self.assertEqual(get_subject_screening_model_cls(), SubjectScreening)

    def test_format_reasons_ineligible(self):
        str_values = ["age_in_years", "on_art"]
        self.assertEqual(format_reasons_ineligible(*str_values), "age_in_years|on_art")

        str_values = ["age_in_years", None, None, "on_art"]
        self.assertEqual(
            format_reasons_ineligible(*str_values, delimiter="|"), "age_in_years|on_art"
        )

        str_values = ["age_in_years", None, None, "on_art"]
        self.assertEqual(
            format_reasons_ineligible(*str_values, delimiter="<BR>"), "age_in_years<BR>on_art"
        )

        str_values = []
        self.assertEqual(format_reasons_ineligible(*str_values, delimiter="<BR>"), None)

        str_values = None
        self.assertEqual(format_reasons_ineligible(str_values, delimiter="<BR>"), None)

    def test_eligibility_display_label(self):
        self.assertEqual(eligibility_display_label(True), ELIGIBLE.upper())
        self.assertEqual(eligibility_display_label(False), NOT_ELIGIBLE)

    def test_age_evaluator(self):
        age_evaluator = AgeEvaluator(age_lower=18, age_lower_inclusive=True)
        self.assertFalse(age_evaluator.eligible())
        self.assertFalse(age_evaluator.eligible(17))
        self.assertTrue(age_evaluator.eligible(18))

        age_evaluator.eligible()
        self.assertEqual(age_evaluator.reasons_ineligible, "Age unknown")

    def test_gender_evaluator(self):
        gender_evaluator = GenderEvaluator(MALE)
        self.assertTrue(gender_evaluator.eligible)
        gender_evaluator = GenderEvaluator("BARK")
        self.assertFalse(gender_evaluator.eligible)

    def test_model(self):
        obj = SubjectScreening.objects.create(age_in_years=25)

        try:
            IdentifierModel.objects.get(identifier=obj.screening_identifier)
        except ObjectDoesNotExist:
            self.fail(f"Identifier unexpectedly not found. {obj.screening_identifier}")

        self.assertTrue(re.match(UUID_PATTERN, obj.subject_identifier))

        screening_identifier = obj.screening_identifier
        obj.save()
        obj.refresh_from_db()
        self.assertEqual(screening_identifier, obj.screening_identifier)

        self.assertTrue(re.match(UUID_PATTERN, obj.subject_identifier))

        obj.subject_identifier = "1234"
        obj.save()
        obj.refresh_from_db()
        self.assertIsNone(re.match(UUID_PATTERN, obj.subject_identifier))

    def test_model_with_screening_eligiblity_cls_missing(self):
        """No criteria is being assessed"""
        self.assertFalse(
            SubjectScreeningWithEligibilitySimple.objects.create(
                age_in_years=25,
            ).eligible
        )

    def test_model_screening_eligiblity_resave(self):
        obj = SubjectScreeningWithEligibility.objects.create(age_in_years=17, alive=NO)
        self.assertFalse(obj.eligible)
        # note model attr is formatted as a string of dict.values()
        self.assertEqual(obj.reasons_ineligible, "must be >=18|must be alive")
        obj.save()
        obj.refresh_from_db()
        self.assertFalse(obj.eligible)
        self.assertEqual(obj.reasons_ineligible, "must be >=18|must be alive")
        obj.age_in_years = 18
        obj.save()
        obj.refresh_from_db()
        self.assertFalse(obj.eligible)
        self.assertEqual(obj.reasons_ineligible, "must be alive")
        obj.alive = YES
        obj.save()
        obj.refresh_from_db()
        self.assertTrue(obj.eligible)
        self.assertEqual(obj.reasons_ineligible, None)
