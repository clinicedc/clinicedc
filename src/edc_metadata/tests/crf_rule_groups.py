from edc_constants.constants import FEMALE, MALE
from edc_metadata import NOT_REQUIRED, REQUIRED
from edc_metadata.metadata_rules import (
    CrfRule,
    CrfRuleGroup,
    P,
)


class CrfRuleGroupWithSourceModel(CrfRuleGroup):
    """Specifies source model."""

    crfs_male = CrfRule(
        predicate=P("f1", "eq", "car"),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_models=["crffive", "crffour"],
    )

    crfs_female = CrfRule(
        predicate=P("f1", "eq", "bicycle"),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_models=["crfthree", "crftwo"],
    )

    class Meta:
        app_label = "tests"
        source_model = "clinicedc_tests.crfone"
        related_visit_model = "edc_visit_tracking.subjectvisit"


class CrfRuleGroupWithoutSourceModel(CrfRuleGroup):
    crfs_male = CrfRule(
        predicate=P("gender", "eq", MALE),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_models=["crffive", "crffour"],
    )

    crfs_female = CrfRule(
        predicate=P("gender", "eq", FEMALE),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_models=["crfthree", "crftwo"],
    )

    class Meta:
        app_label = "tests"
        related_visit_model = "edc_visit_tracking.subjectvisit"


class CrfRuleGroupWithoutExplicitReferenceModel(CrfRuleGroup):
    crfs_male = CrfRule(
        predicate=P("gender", "eq", MALE),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_models=["crffive", "crffour"],
    )

    crfs_female = CrfRule(
        predicate=P("gender", "eq", FEMALE),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_models=["crfthree", "crftwo"],
    )

    class Meta:
        app_label = "tests"
        source_model = "clinicedc_tests.crfone"
        related_visit_model = "edc_visit_tracking.subjectvisit"


class CrfRuleGroupGender(CrfRuleGroup):
    crfs_male = CrfRule(
        predicate=P("gender", "eq", MALE),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_models=["crffour", "crffive"],
    )

    crfs_female = CrfRule(
        predicate=P("gender", "eq", FEMALE),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_models=["crftwo", "crfthree"],
    )

    class Meta:
        app_label = "tests"
        related_visit_model = "edc_visit_tracking.subjectvisit"


class CrfRuleGroupOne(CrfRuleGroup):
    crfs_car = CrfRule(
        predicate=P("f1", "eq", "car"),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_models=["crftwo"],
    )

    crfs_bicycle = CrfRule(
        predicate=P("f3", "eq", "bicycle"),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_models=["crfthree"],
    )

    class Meta:
        app_label = "tests"
        source_model = "clinicedc_tests.crfone"


class CrfRuleGroupTwo(CrfRuleGroup):
    crfs_truck = CrfRule(
        predicate=P("f1", "eq", "truck"),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_models=["crffive"],
    )

    crfs_train = CrfRule(
        predicate=P("f1", "eq", "train"),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_models=["crfsix"],
    )

    class Meta:
        app_label = "tests"
        source_model = "clinicedc_tests.crfone"


class CrfRuleGroupThree(CrfRuleGroup):
    crfs_truck = CrfRule(
        predicate=P("f1", "eq", "holden"),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_models=["prnone"],
    )

    class Meta:
        app_label = "tests"
        source_model = "clinicedc_tests.crfone"
