from collections import OrderedDict, namedtuple

from ..rule_group_meta_options import RuleGroupMetaOptions
from ..rule_group_metaclass import RuleGroupMetaclass
from .requisition_metadata_updater import RequisitionMetadataUpdater

RuleResult = namedtuple('RuleResult', 'target_panel entry_status')


class RequisitionRuleGroupMetaOptionsError(Exception):
    pass


class RequisitionRuleGroupMetaOptions(RuleGroupMetaOptions):

    def __init__(self, group_name, attrs):
        super().__init__(group_name, attrs)
        self.requisition_model = self.options.get('requisition_model')
        if self.requisition_model:
            try:
                assert len(self.requisition_model.split('.')) == 2
            except AssertionError:
                self.requisition_model = f'{self.app_label}.{self.requisition_model}'
                self.options.update(requisition_model=self.requisition_model)
            self.options.update(
                target_models=[self.requisition_model])
            rules = {k: v for k, v in attrs.items() if not k.startswith('_')}
            if self.requisition_model == self.source_model:
                for name, rule in rules.items():
                    if not rule.source_panel:
                        raise RequisitionRuleGroupMetaOptionsError(
                            f'Rule expects "source_panel". Got '
                            f'requisition_model="{self.requisition_model}", '
                            f'source_model="{self.source_model}". '
                            f'See {group_name}.{name}.')
            else:
                for name, rule in rules.items():
                    if rule.source_panel:
                        raise RequisitionRuleGroupMetaOptionsError(
                            f'Rule does not expect "source_panel". Got '
                            f'requisition_model="{self.requisition_model}", '
                            f'source_model="{self.source_model}". '
                            f'See {group_name}.{name}.')

    @property
    def default_meta_options(self):
        opts = super().default_meta_options
        opts.extend(['requisition_model'])
        return opts


class RequisitionMetaclass(RuleGroupMetaclass):

    rule_group_meta = RequisitionRuleGroupMetaOptions


class RequisitionRuleGroup(object, metaclass=RequisitionMetaclass):

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
                    metadata_objects.update({target_panel: metadata_object})
                    rule_results[str(rule)][target_model].append(
                        RuleResult(target_panel, entry_status))
        return rule_results, metadata_objects
