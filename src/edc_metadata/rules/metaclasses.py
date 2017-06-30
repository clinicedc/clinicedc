import copy
import inspect

from .rule import Rule


class RuleGroupError(Exception):
    pass


class RuleGroupMetaError(Exception):
    pass


class RuleGroupMetaOptions:
    """Class to prepare the "meta" instance with the Meta class
    attributes.

    Adds default options if they were not declared on Meta class.

    """

    def __init__(self, group_name, attrs):
        self._source_model = None
        meta = attrs.pop('Meta', None)
        # assert meta class was declared on the rule group
        if not meta:
            raise AttributeError(f'Missing Meta class. See {group_name}')
        # add default options if they do not exist
        for attr in self.default_meta_options:
            try:
                getattr(meta, attr)
            except AttributeError:
                setattr(meta, attr, None)
        # populate options dictionary
        self.options = {
            k: getattr(meta, k) for k in meta.__dict__ if not k.startswith('_')}
        # raise on any unknown attributes declared on the Meta class
        for meta_attr in self.options:
            if meta_attr not in [k for k in self.default_meta_options if not k.startswith('_')]:
                raise RuleGroupMetaError(
                    f'Invalid _meta attr. Got \'{meta_attr}\'. See {group_name}.')
        # default app_label if not declared
        module_name = attrs.get('__module__').split('.')[0]
        self.app_label = self.options.get('app_label', module_name)
        # source_model
        self.source_model = self.options.get('source_model')
        if self.source_model:
            try:
                assert len(self.source_model.split('.')) == 2
            except AssertionError:
                self.source_model = f'{self.app_label}.{self.source_model}'
                self.options.update(source_model=self.source_model)


#     @property
#     def source_model(self):
#         if not self._source_model:
#             self._source_model = self.options.get('source_model')
#             if self._source_model:
#                 try:
#                     self._source_model.split('.')
#                 except AttributeError:
#                     self._source_model = f'{self.app_label}.{self._source_model}'
#         return self._source_model

    @property
    def default_meta_options(self):
        return ['app_label', 'source_model']


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
