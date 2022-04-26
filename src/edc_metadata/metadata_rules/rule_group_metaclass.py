import copy
import inspect
from typing import Any

from .rule import Rule
from .rule_group_meta_options import RuleGroupMetaOptions


class RuleGroupError(Exception):
    pass


class RuleGroupMetaclass(type):
    """Rule group metaclass."""

    rule_group_meta = RuleGroupMetaOptions

    def __new__(mcs, name: str, bases: tuple, attrs: dict) -> Any:
        try:
            abstract = attrs.get("Meta", False).abstract
        except AttributeError:
            abstract = False
        parents = [b for b in bases if isinstance(b, RuleGroupMetaclass)]
        if not parents or abstract:
            # If this isn't a subclass, don't do anything special.
            return super().__new__(mcs, name, bases, attrs)

        # get rules from abstract parents
        for parent in parents:
            try:
                if parent.Meta.abstract:
                    for rule in [
                        member
                        for member in inspect.getmembers(parent)
                        if isinstance(member[1], Rule)
                    ]:
                        parent_rule = copy.deepcopy(rule)
                        attrs.update({parent_rule[0]: parent_rule[1]})
            except AttributeError:
                pass

        # prepare "meta" options from class Meta:
        meta = mcs.rule_group_meta(name, attrs)
        # add the rules tuple to the meta options
        rules = mcs.__get_rules(name, attrs, meta)
        meta.options.update(rules=rules)
        # ... django style _meta
        attrs.update({"_meta": meta})

        attrs.update({"name": f"{meta.app_label}.{name.lower()}"})
        return super().__new__(mcs, name, bases, attrs)

    @classmethod
    def __get_rules(mcs, name: str, attrs: dict, meta: Any) -> tuple:
        """Returns a list of rules after updating each rule's attrs
        with values from Meta.

        Note: Attrs from Meta will overwrite those on rule.
        """
        rules = []
        for key, value in attrs.items():
            if not key.startswith("_"):
                if isinstance(value, Rule):
                    rule = value
                    rule.name = key
                    rule.group = name
                    for k, v in meta.options.items():
                        setattr(rule, k, v)
                    rule.target_models = mcs.__get_target_models(rule, meta)
                    rules.append(rule)
        return tuple(rules)

    @classmethod
    def __get_target_models(mcs, rule: Any, meta: Any) -> Any:
        """Returns target models as a list of label_lowers.

        Target models are the models whose metadata is acted upon.

        If `model_name` instead of `label_lower`, assumes `app_label`
        from meta.app_label.
        """
        target_models = []
        for target_model in rule.target_models:
            if len(target_model.split(".")) != 2:
                target_model = f"{meta.app_label}.{target_model}"
            target_models.append(target_model)
        return target_models
