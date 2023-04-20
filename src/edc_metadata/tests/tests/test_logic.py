from django.test import TestCase

from ...constants import NOT_REQUIRED, REQUIRED
from ...metadata_rules import Logic, RuleLogicError


class MetadataRulesTests(TestCase):
    def test_logic(self):
        logic = Logic(
            predicate=lambda x: True if x else False,
            consequence=REQUIRED,
            alternative=NOT_REQUIRED,
        )
        self.assertTrue(logic.predicate(1) is True)
        self.assertTrue(logic.consequence == REQUIRED)
        self.assertTrue(logic.alternative == NOT_REQUIRED)
        self.assertTrue(repr(logic))

    def test_logic_invalid_consequence(self):
        self.assertRaises(
            RuleLogicError,
            Logic,
            predicate=lambda x: False if x else True,
            consequence="blah",
            alternative=NOT_REQUIRED,
        )

    def test_logic_invalid_alternative(self):
        self.assertRaises(
            RuleLogicError,
            Logic,
            predicate=lambda x: False if x else True,
            consequence=NOT_REQUIRED,
            alternative="blah",
        )

    def test_logic_assert_predicate_is_callable(self):
        self.assertRaises(
            RuleLogicError,
            Logic,
            predicate="erik",
            consequence=REQUIRED,
            alternative=NOT_REQUIRED,
        )
