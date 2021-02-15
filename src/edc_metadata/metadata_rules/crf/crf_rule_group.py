from collections import OrderedDict

from ...metadata_updater import MetadataUpdater
from ...target_handler import TargetModelConflict
from ..rule_group import RuleGroup
from ..rule_group_metaclass import RuleGroupMetaclass


class CrfRuleGroup(RuleGroup, metaclass=RuleGroupMetaclass):
    """A class used to declare and contain rules."""

    metadata_updater_cls = MetadataUpdater

    def __str__(self):
        return f"{self.__class__.__name__}({self.name})"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"

    @classmethod
    def crfs_for_visit(cls, visit=None):
        """Returns a list of scheduled or unscheduled
        CRFs depending on visit_code_sequence.
        """
        if visit.visit_code_sequence != 0:
            crfs = visit.visit.crfs_unscheduled + visit.visit.crfs_prn
        else:
            crfs = visit.visit.crfs + visit.visit.crfs_prn
        return crfs

    @classmethod
    def evaluate_rules(cls, visit=None):
        rule_results = OrderedDict()
        metadata_objects = OrderedDict()
        for rule in cls._meta.options.get("rules"):
            rule_results.update({str(rule): rule.run(visit=visit)})
            for target_model, entry_status in rule_results[str(rule)].items():
                if target_model == visit._meta.label_lower:
                    raise TargetModelConflict(
                        f"Target model and visit model are the same! "
                        f"Got {target_model}=={visit._meta.label_lower}"
                    )
                # only do something if target model is in visit.crfs
                if target_model in [c.model for c in cls.crfs_for_visit(visit)]:
                    metadata_updater = cls.metadata_updater_cls(
                        visit_model_instance=visit, target_model=target_model
                    )
                    metadata_obj = metadata_updater.update(entry_status=entry_status)
                    metadata_objects.update({target_model: metadata_obj})
        return rule_results, metadata_objects
