from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from django.test import TestCase, override_settings, tag

from edc_metadata.constants import NOT_REQUIRED, REQUIRED
from edc_metadata.metadata_rules import Logic, RuleLogicError

utc_tz = ZoneInfo("UTC")


@tag("metadata")
@override_settings(SITE_ID=10)
@time_machine.travel(datetime(2019, 8, 11, 8, 00, tzinfo=utc_tz))
class MetadataRulesTests(TestCase):
    def test_logic(self):
        logic = Logic(
            predicate=lambda x: bool(x),
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
            predicate=lambda x: not x,
            consequence="blah",
            alternative=NOT_REQUIRED,
        )

    def test_logic_invalid_alternative(self):
        self.assertRaises(
            RuleLogicError,
            Logic,
            predicate=lambda x: not x,
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
