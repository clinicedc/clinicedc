from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.consents import consent_v1
from django.test import TestCase, override_settings, tag

from edc_consent import site_consents
from edc_constants.constants import MALE
from edc_facility.import_holidays import import_holidays
from edc_metadata import NOT_REQUIRED, REQUIRED
from edc_metadata.metadata_rules import (
    CrfRule,
    CrfRuleGroup,
    P,
    RegisterRuleGroupError,
    SiteMetadataNoRulesError,
    SiteMetadataRulesAlreadyRegistered,
    register,
    site_metadata_rules,
)

test_datetime = datetime(2019, 6, 11, 8, 00, tzinfo=ZoneInfo("UTC"))


class RuleGroupWithoutRules(CrfRuleGroup):
    class Meta:
        app_label = "clinicedc_tests"
        source_model = "edc_visit_tracking.subjectvisit"


class RuleGroupWithRules(CrfRuleGroup):
    rule1 = CrfRule(
        predicate=P("gender", "eq", MALE),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_models=["crfone", "crftwo"],
    )

    class Meta:
        app_label = "clinicedc_tests"
        source_model = "edc_visit_tracking.subjectvisit"


class RuleGroupWithRules2(CrfRuleGroup):
    rule1 = CrfRule(
        predicate=P("gender", "eq", MALE),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_models=["crfone", "crftwo"],
    )

    class Meta:
        app_label = "clinicedc_tests"
        source_model = "edc_visit_tracking.subjectvisit"


utc_tz = ZoneInfo("UTC")


@tag("metadata")
@override_settings(SITE_ID=10)
@time_machine.travel(datetime(2019, 8, 11, 8, 00, tzinfo=utc_tz))
class TestSiteMetadataRules(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self):
        site_metadata_rules.registry = {}
        site_consents.registry = {}
        site_consents.register(consent_v1)

    def test_register_rule_group_no_rules_raises_on_register(self):
        self.assertRaises(
            SiteMetadataNoRulesError,
            site_metadata_rules.register,
            RuleGroupWithoutRules,
        )

    def test_register_rule_group_with_rule(self):
        try:
            site_metadata_rules.register(RuleGroupWithRules)
        except SiteMetadataNoRulesError:
            self.fail("SiteMetadataNoRulesError unexpectedly raised.")

    def test_register_rule_group_get_rule_groups_for_app_label(self):
        site_metadata_rules.register(RuleGroupWithRules)
        rule_groups = site_metadata_rules.rule_groups.get("clinicedc_tests")
        self.assertEqual(rule_groups, [RuleGroupWithRules])

    def test_register_rule_group_register_more_than_one_rule_group(self):
        site_metadata_rules.register(RuleGroupWithRules)
        site_metadata_rules.register(RuleGroupWithRules2)
        rule_groups = site_metadata_rules.rule_groups.get("clinicedc_tests")
        self.assertEqual(rule_groups, [RuleGroupWithRules, RuleGroupWithRules2])

    def test_register_twice_raises(self):
        site_metadata_rules.register(rule_group_cls=RuleGroupWithRules)
        self.assertRaises(
            SiteMetadataRulesAlreadyRegistered,
            site_metadata_rules.register,
            RuleGroupWithRules,
        )

    def test_rule_group_repr(self):
        repr(RuleGroupWithRules())
        str(RuleGroupWithRules())

    def test_register_decorator(self):
        @register()
        class RuleGroupWithRules(CrfRuleGroup):
            rule1 = CrfRule(
                predicate=P("gender", "eq", MALE),
                consequence=REQUIRED,
                alternative=NOT_REQUIRED,
                target_models=["crfone", "crftwo"],
            )

            class Meta:
                app_label = "clinicedc_tests"
                source_model = "edc_visit_tracking.subjectvisit"

        self.assertIn("clinicedc_tests", site_metadata_rules.registry)

    def test_register_decorator_raises(self):
        try:

            @register()
            class RuleGroupWithRules:
                class Meta:
                    app_label = "clinicedc_tests"
                    source_model = "edc_visit_tracking.subjectvisit"

        except RegisterRuleGroupError:
            pass
        else:
            self.fail("RegisterRuleGroupError unexpectedly not raised.")
