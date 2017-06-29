from collections import OrderedDict, namedtuple

from ..rule_group import RuleGroup
from .requisition_metadata_updater import RequisitionMetadataUpdater

RuleResult = namedtuple('RuleResult', 'target_panel entry_status')


class RequisitionRuleGroup(RuleGroup):

    metadata_updater_cls = RequisitionMetadataUpdater

    @classmethod
    def evaluate_rules(cls, visit=None):
        """Returns a tuple of (rule_results, metadata_objects) where
        rule_results ....
        """
        rule_results = OrderedDict()
        metadata_objects = OrderedDict()
        metadata_updater = cls.metadata_updater_cls(visit=visit)
        for rule in cls._meta.options.get('rules'):
            rule_results[str(rule)] = OrderedDict()
            for target_model, entry_status in rule.run(visit=visit).items():
                rule_results[str(rule)].update({target_model: []})
                for target_panel in rule.target_panels:
                    metadata_object = metadata_updater.update(
                        target_model=target_model,
                        target_panel=target_panel,
                        entry_status=entry_status)
                    metadata_objects.update({target_model: metadata_object})
                    rule_results[str(rule)][target_model].append(
                        RuleResult(target_panel, entry_status))
        return rule_results, metadata_objects

    class Meta:
        abstract = True
