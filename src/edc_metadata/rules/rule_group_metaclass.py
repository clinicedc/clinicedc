import copy
import inspect

from .rule import Rule
from .rule_group_meta_options import RuleGroupMetaOptions


class RuleGroupError(Exception):
    pass


class RuleGroupMetaclass(type):
    """Rule group metaclass.
    """

    rule_group_meta = RuleGroupMetaOptions

    def __new__(cls, name, bases, attrs):
        """Add the Meta attributes to each rule.
        """
        try:
            abstract = attrs.get('Meta', False).abstract
        except AttributeError:
            abstract = False
        parents = [b for b in bases if isinstance(b, RuleGroupMetaclass)]
        if not parents or abstract:
            # If this isn't a subclass of BaseRuleGroup, don't do anything
            # special.
            return super().__new__(cls, name, bases, attrs)
        for parent in parents:
            try:
                if parent.Meta.abstract:
                    for rule in [member for member in inspect.getmembers(parent)
                                 if isinstance(member[1], Rule)]:
                        parent_rule = copy.deepcopy(rule)
                        attrs.update({parent_rule[0]: parent_rule[1]})
            except AttributeError:
                pass

        # get meta options
        meta = cls.rule_group_meta(name, attrs)

        # update rules tuple to meta options
        rules = cls.__get_rules(name, attrs, meta)
        meta.options.update(rules=rules)

        attrs.update({'_meta': meta})
        attrs.update(
            {'name': f'{meta.app_label}.{name.lower()}'})
        return super().__new__(cls, name, bases, attrs)

    @classmethod
    def __get_rules(cls, name, attrs, meta):
        """Update attrs in each rule from values in Meta.
        """
        rules = []
        for rule_name, rule in attrs.items():
            if not rule_name.startswith('_'):
                if isinstance(rule, Rule):
                    rule.name = rule_name
                    rule.group = name
                    for k, v in meta.options.items():
                        setattr(rule, k, v)
                    rule.target_models = cls.__get_target_models(rule, meta)
                    rules.append(rule)
        return tuple(rules)

    @classmethod
    def __get_target_models(cls, rule, meta):
        """Returns target models as list of label_lower.

        Target models are the models whose metadata is acted upon.

        If `model_name` instead of `label_lower`, assumes `app_label`
        from meta.app_label.

        Accepts rule attr `target_model` or `target_models`.
        """
        target_models = []
        for target_model in rule.target_models:
            if len(target_model.split('.')) != 2:
                target_model = (
                    f'{meta.app_label}.{target_model}')
            target_models.append(target_model)
        return target_models
