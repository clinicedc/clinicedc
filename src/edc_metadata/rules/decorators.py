from .rule_group import RuleGroup
from .site_rule_groups import site_rule_groups


def register(site=None, **kwargs):
    """
    Registers a rule group
    """
    site = site or site_rule_groups

    def _rule_group_wrapper(rule_group_class):

        if not issubclass(rule_group_class, RuleGroup):
            raise ValueError('Wrapped class must RuleGroup.')

        site.register(rule_group_class)

        return rule_group_class
    return _rule_group_wrapper
