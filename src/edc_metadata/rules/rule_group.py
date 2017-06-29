import copy
import inspect

from collections import OrderedDict

from .metadata_updater import MetadataUpdater
from .rule import Rule


class RuleGroupError(Exception):
    pass


class RuleGroupMetaError(Exception):
    pass


class RuleGroupModelConflict(Exception):
    pass


class RuleGroupMeta:
    """Base class for RuleGroup "Meta" class.
    """

    app_label = None
    source_model = None

    def __init__(self, group_name, attrs):
        self.options = self.__get_meta_attrs(group_name, attrs)
        for k, v in self.options.items():
            setattr(self, k, v)
        self.group_name = group_name

    def __repr__(self):
        return (f'<{self.__class__.__name__}({self.group_name}), '
                f'source_model={self.source_model}>')

    def __get_meta_attrs(self, name, attrs):
        meta = attrs.pop('Meta', None)
        if not meta:
            raise AttributeError(f'Missing Meta class. See {name}')
        for attr in RuleGroupMeta.__dict__:
            try:
                getattr(meta, attr)
            except AttributeError:
                setattr(meta, attr, None)
        meta_attrs = {
            k: getattr(meta, k) for k in meta.__dict__ if not k.startswith('_')}
        for meta_attr in meta_attrs:
            if meta_attr not in [k for k in RuleGroupMeta.__dict__ if not k.startswith('_')]:
                raise RuleGroupMetaError(
                    f'Invalid _meta attr. Got \'{meta_attr}\'. See {name}.')
        return meta_attrs


class RuleGroupMetaClass(type):
    """Rule group metaclass.
    """

    rule_group_meta = RuleGroupMeta

    def __new__(cls, name, bases, attrs):
        """Add the Meta attributes to each rule.
        """
        try:
            abstract = attrs.get('Meta', False).abstract
        except AttributeError:
            abstract = False
        parents = [b for b in bases if isinstance(b, RuleGroupMetaClass)]
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
        attrs.update({'name': f'{meta.app_label}.{name.lower()}'})
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
        if meta.source_model in target_models:
            raise RuleGroupModelConflict(
                f'Source model cannot be a target model. Got \'{meta.source_model}\' '
                f'is in target models {target_models}')
        return target_models


class RuleGroup(object, metaclass=RuleGroupMetaClass):
    """A class used to declare and contain rules.
    """

    metadata_updater_cls = MetadataUpdater

    def __str__(self):
        return f'{self.__class__.__name__}({self.name})'

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name})'

    @classmethod
    def evaluate_rules(cls, visit=None):
        rule_results = OrderedDict()
        metadata_objects = OrderedDict()
        metadata_updater = cls.metadata_updater_cls(visit=visit)
        for rule in cls._meta.options.get('rules'):
            rule_results.update({str(rule): rule.run(visit=visit)})
            for target_model, entry_status in rule_results[str(rule)].items():
                metadata_object = metadata_updater.update(
                    target_model=target_model,
                    entry_status=entry_status)
                metadata_objects.update({target_model: metadata_object})
        return rule_results, metadata_objects
