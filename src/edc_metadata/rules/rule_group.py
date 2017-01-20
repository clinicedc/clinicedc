import inspect
import copy

from .exceptions import RuleGroupError
from .rule import Rule


class BaseMeta:
    """Base class for RuleGroup "Meta" class."""

    app_label = None
    source_model = None
    source_fk = None
    rules = None

    def __init__(self, group_name, **meta_attrs):
        for k, v in meta_attrs.items():
            setattr(self, k, v)
        self.group_name = group_name

    def __repr__(self):
        return '<Options for {}>'.format(self.group_name)


class RuleGroupMeta(type):
    """Rule group metaclass."""

    def __new__(cls, name, bases, attrs):
        """Add the Meta attributes to each rule."""
        try:
            abstract = attrs.get('Meta', False).abstract
        except AttributeError:
            abstract = False
        parents = [b for b in bases if isinstance(b, RuleGroupMeta)]
        if not parents or abstract:
            # If this isn't a subclass of BaseRuleGroup, don't do anything special.
            return super(RuleGroupMeta, cls).__new__(cls, name, bases, attrs)
        for parent in parents:
            try:
                if parent.Meta.abstract:
                    for rule in [member for member in inspect.getmembers(parent) if isinstance(member[1], Rule)]:
                        parent_rule = copy.deepcopy(rule)
                        attrs.update({parent_rule[0]: parent_rule[1]})
            except AttributeError:
                pass

        # get the meta class delared on the RuleGroup
        meta = attrs.pop('Meta', None)

        try:
            if meta.source_model == meta.source_model.split('.'):
                source_model = meta.app_label, meta.source_model
            else:
                source_model = meta.source_model.split('.')
        except AttributeError as e:
            if '\'tuple\' object has no attribute \'split\'' not in str(e):
                meta.source_model = None
                source_model = None
            else:
                source_model = meta.source_model

        try:
            if not meta.source_fk:
                meta.source_fk = None
        except AttributeError:
            meta.source_fk = None

        # update attrs in each rule from values in Meta
        rules = []
        for rule_name, rule in attrs.items():
            if not rule_name.startswith('_'):
                if isinstance(rule, Rule):
                    rule.name = rule_name
                    rule.group = name
                    rule.app_label = meta.app_label
                    if meta:
                        rule.app_label = meta.app_label
                        target_models = []
                        try:
                            for target_model in rule.target_models:
                                if len(target_model.split('.')) != 2:
                                    target_model = '{}.{}'.format(meta.app_label, target_model)
                                target_models.append(target_model)
                            rule.target_models = target_models
                        except AttributeError as e:
                            if 'target_models' not in str(e):
                                raise AttributeError(e)
                            if len(rule.target_model.split('.')) != 2:
                                rule.target_model = '{}.{}'.format(meta.app_label, rule.target_model)
                            rule.target_models = [rule.target_model]
                        rule.source_model = source_model
                        rules.append(rule)
        # add a django like _meta to Rulegroup as an instance of BaseMeta
        meta_attrs = {k: getattr(meta, k) for k in meta.__dict__ if not k.startswith('_')}
        meta_attrs.update({'rules': tuple(rules)})
        attrs.update({'_meta': BaseMeta(name, **meta_attrs)})
        attrs.update({'name': '{}.{}'.format(meta.app_label, name.lower())})
        return super(RuleGroupMeta, cls).__new__(cls, name, bases, attrs)


class RuleGroup(object, metaclass=RuleGroupMeta):
    """A class used to declare and contain rules."""

    @classmethod
    def run_for_source_model(cls, obj, source_model):
        for rule in cls._meta.rules:
            if rule.source_model == source_model:
                try:
                    rule.run(obj)
                except AttributeError as e:
                    raise RuleGroupError(
                        'An exception was raised for rule {} with object \'{}\'. Got {}'.format(
                            rule, obj._meta.label_lower, str(e)))

    @classmethod
    def run_all(cls, obj):
        for rule in cls._meta.rules:
            try:
                rule.run(obj)
            except AttributeError as e:
                raise RuleGroupError(
                    'An exception was raised for rule {} with object \'{}\'. Got {}'.format(
                        rule, obj._meta.label_lower, str(e)))
