from typing import Any

from .crf import CrfRuleGroup
from .requisition import RequisitionRuleGroup
from .site import site_metadata_rules


class RegisterRuleGroupError(Exception):
    pass


def register(site=None, **kwargs) -> Any:  # noqa
    """Registers a rule group."""
    site = site or site_metadata_rules

    def _rule_group_wrapper(rule_group_cls: Any) -> Any:
        if not issubclass(rule_group_cls, (CrfRuleGroup, RequisitionRuleGroup)):
            raise RegisterRuleGroupError(
                f"Wrapped class must a RuleGroup class. Got {rule_group_cls}"
            )

        site.register(rule_group_cls=rule_group_cls)

        return rule_group_cls

    return _rule_group_wrapper
