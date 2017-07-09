from collections import OrderedDict

from ...constants import CRF
from ..rule_group_metaclass import RuleGroupMetaclass
from ..metadata_updater import MetadataUpdater


class CrfRuleGroup(object, metaclass=RuleGroupMetaclass):
    """A class used to declare and contain rules.
    """

    metadata_updater_cls = MetadataUpdater
    metadata_category = CRF

    def __str__(self):
        return f'{self.__class__.__name__}({self.name})'

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name})'

    @classmethod
    def evaluate_rules(cls, visit=None):
        rule_results = OrderedDict()
        metadata_objects = OrderedDict()
        metadata_updater = cls.metadata_updater_cls(
            visit=visit, metadata_category=cls.metadata_category)
        for rule in cls._meta.options.get('rules'):
            rule_results.update({str(rule): rule.run(visit=visit)})
            for target_model, entry_status in rule_results[str(rule)].items():
                metadata_object = metadata_updater.update(
                    target_model=target_model,
                    entry_status=entry_status)
                metadata_objects.update({target_model: metadata_object})
        return rule_results, metadata_objects
