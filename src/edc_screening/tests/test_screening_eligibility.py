from django.test import TestCase
from edc_constants.constants import NO, TBD, YES

from edc_screening.exceptions import (
    ScreeningEligibilityAttributeError,
    ScreeningEligibilityError,
    ScreeningEligibilityInvalidCombination,
    ScreeningEligibilityModelAttributeError,
)
from edc_screening.fc import FC
from edc_screening.screening_eligibility import (
    ScreeningEligibility as BaseScreeningEligibility,
)

from .models import SubjectScreening


class TestScreening(TestCase):
    def test_fc(self):
        fc = FC()
        self.assertTrue(repr(fc))
        self.assertTrue(str(fc))

    def test_repr_and_str(self):
        class ScreeningEligibility(BaseScreeningEligibility):
            pass

        eligibility = ScreeningEligibility()
        self.assertTrue(repr(eligibility))
        self.assertTrue(str(eligibility))

    def test_without_required_fields_or_assess_eligibility(self):
        """Assert that the base screening class, if not modified,
        does nothing.
        """

        class ScreeningEligibility(BaseScreeningEligibility):
            pass

        eligibility = ScreeningEligibility()
        self.assertDictEqual(eligibility.reasons_ineligible, {})
        self.assertFalse(eligibility.is_eligible)
        self.assertEqual(eligibility.eligible, TBD)

    def test_required_fields_does_not_have_corresponding_class_attr(self):
        required_fields = dict(erik=FC(YES, "erik must be YES", ignore_if_missing=True))

        class ScreeningEligibility(BaseScreeningEligibility):
            def get_required_fields(self):
                return required_fields

        cleaned_data = {}
        self.assertRaises(
            ScreeningEligibilityAttributeError,
            ScreeningEligibility,
            cleaned_data=cleaned_data,
        )

    def test_required_fields_has_corresponding_class_attr(self):
        required_fields = dict(erik=FC(YES, "erik must be YES"))

        class ScreeningEligibility(BaseScreeningEligibility):
            def __init__(self, **kwargs):
                self.erik = None
                super().__init__(**kwargs)

            def get_required_fields(self):
                return required_fields

        cleaned_data = dict(erik=YES)
        try:
            ScreeningEligibility(cleaned_data=cleaned_data)
        except ScreeningEligibilityAttributeError:
            self.fail("ScreeningEligibilityAttributeError unexpectedly raised")

    def test_required_fields_does_not_have_corresponding_model_attr(self):
        model_obj = SubjectScreening.objects.create(age_in_years=25)
        required_fields = dict(erik=FC(NO, "erik must be YES"))

        class ScreeningEligibility(BaseScreeningEligibility):
            def __init__(self, **kwargs):
                self.erik = None
                super().__init__(**kwargs)

            def get_required_fields(self):
                return required_fields

        self.assertRaises(
            ScreeningEligibilityModelAttributeError, ScreeningEligibility, model_obj=model_obj
        )

    def test_with_model_obj(self):
        model_obj = SubjectScreening.objects.create(thing="thing", age_in_years=25)
        required_fields = dict(thing=FC(YES, "thing must be YES"))

        class ScreeningEligibility(BaseScreeningEligibility):
            def __init__(self, **kwargs):
                self.thing = None
                super().__init__(**kwargs)

            def get_required_fields(self):
                return required_fields

        ScreeningEligibility(model_obj=model_obj)

    def test_with_cleaned_data(self):
        cleaned_data = dict(erik=NO)
        required_fields = dict(erik=FC(YES, "erik must be YES"))

        class ScreeningEligibility(BaseScreeningEligibility):
            def __init__(self, **kwargs):
                self.erik = None
                super().__init__(**kwargs)

            def get_required_fields(self):
                return required_fields

        ScreeningEligibility(cleaned_data=cleaned_data)

    def test_not_eligible(self):
        cleaned_data = dict(erik=NO)
        required_fields = dict(erik=FC(YES, "erik must be YES"))

        class ScreeningEligibility(BaseScreeningEligibility):
            def __init__(self, **kwargs):
                self.erik = None
                super().__init__(**kwargs)

            def get_required_fields(self):
                return required_fields

        eligibility = ScreeningEligibility(cleaned_data=cleaned_data)
        self.assertIn("erik", eligibility.reasons_ineligible)
        self.assertEqual(NO, eligibility.eligible)
        self.assertFalse(eligibility.is_eligible)

    def test_eligible(self):
        cleaned_data = dict(erik=YES)
        required_fields = dict(erik=FC(YES, "erik must be YES"))

        class ScreeningEligibility(BaseScreeningEligibility):
            def __init__(self, **kwargs):
                self.erik = None
                super().__init__(**kwargs)

            def get_required_fields(self):
                return required_fields

        eligibility = ScreeningEligibility(cleaned_data=cleaned_data)
        self.assertNotIn("erik", eligibility.reasons_ineligible)
        self.assertEqual(YES, eligibility.eligible)
        self.assertTrue(eligibility.is_eligible)

    def test_custom_assessment(self):
        cleaned_data = dict(erik=YES, thing_one="maybe")
        required_fields = dict(erik=FC(YES, "erik must be YES"))

        class ScreeningEligibility(BaseScreeningEligibility):
            def __init__(self, **kwargs):
                self.erik = None
                super().__init__(**kwargs)

            def get_required_fields(self):
                return required_fields

            def assess_eligibility(self) -> None:
                if self.cleaned_data.get("thing_one") == "maybe" and self.eligible:
                    self.eligible = TBD
                    self.reasons_ineligible.update(thing_one="thing one not sure")

        eligibility = ScreeningEligibility(cleaned_data=cleaned_data)
        self.assertIn("thing_one", eligibility.reasons_ineligible)
        self.assertEqual(TBD, eligibility.eligible)
        self.assertFalse(eligibility.is_eligible)

    def test_invalid_value_for_eligible(self):
        cleaned_data = dict(erik=YES, thing_one="maybe")
        required_fields = dict(erik=FC(YES, "erik must be YES"))

        class ScreeningEligibility(BaseScreeningEligibility):
            def __init__(self, **kwargs):
                self.erik = None
                super().__init__(**kwargs)

            def get_required_fields(self):
                return required_fields

            def assess_eligibility(self) -> None:
                if self.cleaned_data.get("thing_one") == "maybe" and self.eligible == YES:
                    self.eligible = "BAD DOG"
                    self.reasons_ineligible.update(thing_one="thing one not sure")

        self.assertRaises(
            ScreeningEligibilityError, ScreeningEligibility, cleaned_data=cleaned_data
        )

    def test_invalid_combination_eligible_and_reasons(self):
        cleaned_data = dict(erik=YES, thing_one="maybe")
        required_fields = dict(erik=FC(YES, "erik must be YES"))

        class ScreeningEligibility(BaseScreeningEligibility):
            def __init__(self, **kwargs):
                self.erik = None
                super().__init__(**kwargs)

            def get_required_fields(self):
                return required_fields

            def assess_eligibility(self) -> None:
                if self.cleaned_data.get("thing_one") == "maybe":
                    self.eligible = YES
                    self.reasons_ineligible.update(thing_one="thing one not sure")

        self.assertRaises(
            ScreeningEligibilityInvalidCombination,
            ScreeningEligibility,
            cleaned_data=cleaned_data,
        )

    def test_cannot_override_if_ineligible(self):
        """Assert does not call `assess_eligibility` if default assessment
        is ineligible
        """
        cleaned_data = dict(erik=NO, thing_one="maybe")
        required_fields = dict(erik=FC(YES, "erik must be YES"))

        class ScreeningEligibility(BaseScreeningEligibility):
            def __init__(self, **kwargs):
                self.erik = None
                super().__init__(**kwargs)

            def get_required_fields(self):
                return required_fields

            def assess_eligibility(self) -> None:
                self.eligible = YES
                self.reasons_ineligible = {}

        eligibility = ScreeningEligibility(cleaned_data=cleaned_data)
        self.assertIn("erik", eligibility.reasons_ineligible)
        self.assertEqual(NO, eligibility.eligible)
        self.assertFalse(eligibility.is_eligible)

    def test_options(self):
        required_fields = dict(erik=FC(YES, "erik must be YES"))
        options = {
            "eligible_value_default": "PENDING",
            "eligible_values_list": ["YEAH", "NOPE", "PENDING"],
            "is_eligible_value": "YEAH",
            "is_ineligible_value": "NOPE",
        }

        class ScreeningEligibility(BaseScreeningEligibility):
            def __init__(self, **kwargs):
                self.erik = None
                super().__init__(**kwargs)

            def get_required_fields(self):
                return required_fields

        cleaned_data = dict(erik=YES)
        eligibility = ScreeningEligibility(cleaned_data=cleaned_data, **options)
        self.assertEqual(eligibility.eligible, "YEAH")

        cleaned_data = dict(erik=NO)
        eligibility = ScreeningEligibility(cleaned_data=cleaned_data, **options)
        self.assertEqual(eligibility.eligible, "NOPE")

    def test_formatted(self):
        required_fields = dict(
            thing_one=FC(YES, "thing one must be YES"),
            thing_two=FC(YES, "thing two must be YES"),
        )

        class ScreeningEligibility(BaseScreeningEligibility):
            def __init__(self, **kwargs):
                self.thing_one = None
                self.thing_two = None
                super().__init__(**kwargs)

            def get_required_fields(self):
                return required_fields

        cleaned_data = dict(thing_one=NO, thing_two=NO)
        eligibility = ScreeningEligibility(cleaned_data=cleaned_data)
        self.assertEqual(
            eligibility.formatted_reasons_ineligible(),
            "thing one must be YES<BR>thing two must be YES",
        )

        cleaned_data = dict(thing_one=YES, thing_two=YES)
        eligibility = ScreeningEligibility(cleaned_data=cleaned_data)
        self.assertEqual(eligibility.formatted_reasons_ineligible(), "")

    def test_fc_with_callable(self):
        required_fields = dict(
            age_in_years=FC(lambda x: x >= 18, "must be >=18y"),
        )

        class ScreeningEligibility(BaseScreeningEligibility):
            def __init__(self, **kwargs):
                self.age_in_years = None
                super().__init__(**kwargs)

            def get_required_fields(self):
                return required_fields

        cleaned_data = dict(age_in_years=17)
        eligibility = ScreeningEligibility(cleaned_data=cleaned_data)
        self.assertFalse(eligibility.is_eligible)

        cleaned_data = dict(age_in_years=18)
        eligibility = ScreeningEligibility(cleaned_data=cleaned_data)
        self.assertTrue(eligibility.is_eligible)

    def test_eligibility_display_label(self):
        required_fields = dict(
            thing_one=FC(YES, "thing one must be YES"),
        )

        class ScreeningEligibility(BaseScreeningEligibility):
            def __init__(self, **kwargs):
                self.thing_one = None
                super().__init__(**kwargs)

            def get_required_fields(self):
                return required_fields

        cleaned_data = dict(thing_one=NO)
        eligibility = ScreeningEligibility(
            cleaned_data=cleaned_data, eligible_display_label="E", ineligible_display_label="I"
        )
        self.assertEqual(eligibility.display_label, "I")

        cleaned_data = dict(thing_one=YES)
        eligibility = ScreeningEligibility(
            cleaned_data=cleaned_data, eligible_display_label="E", ineligible_display_label="I"
        )
        self.assertEqual(eligibility.display_label, "E")

    def test_missing_data(self):
        required_fields = dict(
            thing_one=FC(YES, "thing one must be YES"),
            thing_two=FC(ignore_if_missing=True),
            thing_three=FC(YES, "thing two must be YES"),
        )

        class ScreeningEligibility(BaseScreeningEligibility):
            def __init__(self, **kwargs):
                self.thing_one = None
                self.thing_two = None
                self.thing_three = None
                super().__init__(**kwargs)

            def get_required_fields(self):
                return required_fields

        cleaned_data = dict(
            thing_one=YES,
            thing_two=None,
            thing_three=None,
        )
        eligibility = ScreeningEligibility(
            cleaned_data=cleaned_data, eligible_display_label="E", ineligible_display_label="I"
        )

        self.assertNotIn("thing_one", eligibility.reasons_ineligible)
        self.assertNotIn("thing_two", eligibility.reasons_ineligible)
        self.assertIn("thing_three", eligibility.reasons_ineligible)
        self.assertEqual(eligibility.display_label, eligibility.eligible_value_default)

        # assert has enough to know ineligible (thing_one=NO)
        cleaned_data = dict(
            thing_one=NO,
            thing_two=None,
            thing_three=None,
        )
        eligibility = ScreeningEligibility(
            cleaned_data=cleaned_data, eligible_display_label="E", ineligible_display_label="I"
        )

        self.assertIn("thing_one", eligibility.reasons_ineligible)
        self.assertNotIn("thing_two", eligibility.reasons_ineligible)
        self.assertIn("thing_three", eligibility.reasons_ineligible)
        self.assertEqual(eligibility.eligible, eligibility.is_ineligible_value)

    def test_missing_data_with_custom_missing_value(self):
        required_fields = dict(
            thing_one=FC(YES, "thing one must be YES"),
            thing_two=FC(YES, missing_value="NOT_ANSWERED"),
        )

        class ScreeningEligibility(BaseScreeningEligibility):
            def __init__(self, **kwargs):
                self.thing_one = None
                self.thing_two = None
                super().__init__(**kwargs)

            def get_required_fields(self):
                return required_fields

        cleaned_data = dict(
            thing_one=YES,
            thing_two=YES,
        )
        eligibility = ScreeningEligibility(
            cleaned_data=cleaned_data, eligible_display_label="E", ineligible_display_label="I"
        )

        self.assertNotIn("thing_one", eligibility.reasons_ineligible)
        self.assertNotIn("thing_two", eligibility.reasons_ineligible)

        required_fields = dict(
            thing_one=FC(YES, "thing one must be YES"),
            thing_two=FC("NOT_ANSWERED", missing_value="NOT_ANSWERED"),
        )

        cleaned_data = dict(
            thing_one=YES,
            thing_two="NOT_ANSWERED",
        )
        eligibility = ScreeningEligibility(cleaned_data=cleaned_data)

        self.assertNotIn("thing_one", eligibility.reasons_ineligible)
        self.assertIn("thing_two", eligibility.reasons_ineligible)
        self.assertIn("not answered", eligibility.reasons_ineligible.get("thing_two"))

        cleaned_data = dict(
            thing_one=YES,
            thing_two=None,
        )
        eligibility = ScreeningEligibility(cleaned_data=cleaned_data)

        self.assertNotIn("thing_one", eligibility.reasons_ineligible)
        self.assertIn("thing_two", eligibility.reasons_ineligible)
        self.assertIn("not answered", eligibility.reasons_ineligible.get("thing_two"))

    def test_invalid_combinations(self):
        class ScreeningEligibility(BaseScreeningEligibility):
            def __init__(self, **kwargs):
                self.thing_one = None
                super().__init__(**kwargs)

            def get_required_fields(self):
                return {"thing_one": FC(YES, "thing one must be YES")}

            def assess_eligibility(self) -> None:
                self.reasons_ineligible.update(thing_one="who me?")

        cleaned_data = dict(thing_one=YES)
        self.assertRaises(
            ScreeningEligibilityInvalidCombination,
            ScreeningEligibility,
            cleaned_data=cleaned_data,
        )

    def test_invalid_combinations2(self):
        class ScreeningEligibility(BaseScreeningEligibility):
            def __init__(self, **kwargs):
                self.thing_one = None
                super().__init__(**kwargs)

            def get_required_fields(self):
                return {"thing_one": FC(YES, "thing one must be YES")}

            def assess_eligibility(self) -> None:
                self.eligible = NO

        cleaned_data = dict(thing_one=YES)
        self.assertRaises(
            ScreeningEligibilityInvalidCombination,
            ScreeningEligibility,
            cleaned_data=cleaned_data,
        )

    def test_invalid_assess_eligibility(self):
        class ScreeningEligibility(BaseScreeningEligibility):
            def __init__(self, **kwargs):
                self.thing_one = None
                super().__init__(**kwargs)

            def get_required_fields(self):
                return {"thing_one": FC(YES, "thing one must be YES")}

            def assess_eligibility(self) -> None:
                self.eligible = None

        cleaned_data = dict(thing_one=YES)
        self.assertRaises(
            ScreeningEligibilityError,
            ScreeningEligibility,
            cleaned_data=cleaned_data,
        )
