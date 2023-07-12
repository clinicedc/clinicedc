from __future__ import annotations

from typing import TYPE_CHECKING, Any, Tuple

from ...constants import NOT_REQUIRED, REQUIRED
from ...metadata_updater import MetadataUpdater
from ..rule_group import RuleGroup, RuleGroupError, TargetModelConflict
from ..rule_group_metaclass import RuleGroupMetaclass

if TYPE_CHECKING:
    from edc_visit_schedule import FormsCollection
    from edc_visit_tracking.model_mixins import VisitModelMixin as Base

    from ...model_mixins.creates import CreatesMetadataModelMixin
    from ...models import CrfMetadata

    class RelatedVisitModel(CreatesMetadataModelMixin, Base):
        pass


class CrfRuleGroup(RuleGroup, metaclass=RuleGroupMetaclass):
    """A class used to declare and contain rules."""

    metadata_updater_cls = MetadataUpdater

    def __str__(self: Any):
        return f"{self.__class__.__name__}({self.name})"

    def __repr__(self: Any):
        return f"{self.__class__.__name__}({self.name})"

    @classmethod
    def crfs_for_visit(cls, visit=None) -> FormsCollection:
        """Returns a list of scheduled or unscheduled
        CRFs + PRNs depending on visit_code_sequence.
        """
        if visit.visit_code_sequence != 0:
            crfs = visit.visit.crfs_unscheduled + visit.visit.crfs_prn
        else:
            crfs = visit.visit.crfs + visit.visit.crfs_prn
        return crfs

    @classmethod
    def evaluate_rules(
        cls: Any,
        related_visit: RelatedVisitModel = None,
        allow_create: bool | None = None,
    ) -> Tuple[dict[str, dict[str, dict]], dict[str, CrfMetadata]]:
        rule_results = {}
        metadata_objects = {}
        for rule in cls._meta.options.get("rules"):
            # skip if source model is not in visit.crfs (including PRNs)
            if (
                rule.source_model
                and rule.source_model != related_visit._meta.label_lower
                and rule.source_model
                not in [c.model for c in cls.crfs_for_visit(related_visit)]
            ):
                continue
            if result := rule.run(related_visit=related_visit):
                rule_results.update({str(rule): result})
                for target_model, entry_status in rule_results[str(rule)].items():
                    if not entry_status:
                        raise RuleGroupError("Cannot be None. Got `entry_status`.")
                    if target_model == related_visit._meta.label_lower:
                        raise TargetModelConflict(
                            f"Target model and visit model are the same! "
                            f"Got {target_model}=={related_visit._meta.label_lower}"
                        )
                    # only do something if target model is in visit.crfs (including PRNs)
                    if target_model in [c.model for c in cls.crfs_for_visit(related_visit)]:
                        metadata_updater = cls.metadata_updater_cls(
                            related_visit=related_visit,
                            target_model=target_model,
                            allow_create=allow_create,
                        )
                        metadata_obj = metadata_updater.get_and_update(
                            entry_status=entry_status
                        )
                        metadata_objects.update({target_model: metadata_obj})
        return rule_results, metadata_objects

    @classmethod
    def default_entry_status(
        cls, related_visit: RelatedVisitModel, target_model: Any
    ) -> str | None:
        """Returns the default `entry_status` or None"""
        for c in cls.crfs_for_visit(related_visit):
            if c.model == target_model:
                return REQUIRED if c.required else NOT_REQUIRED
        return None
