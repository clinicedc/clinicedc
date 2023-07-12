from __future__ import annotations

from typing import TYPE_CHECKING, Type

from edc_appointment.constants import MISSED_APPT

from .logic import Logic
from .rule_evaluator import RuleEvaluator

if TYPE_CHECKING:
    from edc_reference import ReferenceGetter
    from edc_visit_tracking.model_mixins import VisitModelMixin as Base

    from ..model_mixins.creates import CreatesMetadataModelMixin
    from .predicate import PF, P

    class RelatedVisitModel(CreatesMetadataModelMixin, Base):
        pass


class RuleError(Exception):
    pass


class Rule:
    rule_evaluator_cls = RuleEvaluator
    logic_cls = Logic

    def __init__(
        self,
        predicate: P | PF | callable = None,
        consequence: str = None,
        alternative: str = None,
    ) -> None:
        self._logic: Logic = self.logic_cls(
            predicate=predicate, consequence=consequence, alternative=alternative
        )
        self.target_models: list[str] | None = None
        self.app_label: str | None = None  # set by metaclass
        self.group = None  # set by metaclass
        self.name: str | None = None  # set by metaclass
        self.source_model: str | None = None  # set by metaclass
        self.reference_getter_cls: Type[ReferenceGetter] | None = None  # set by metaclass
        self.field_names = []
        try:
            self.field_names = [predicate.attr]
        except AttributeError:
            try:
                self.field_names = predicate.attrs
            except AttributeError:
                pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', group='{self.group}')"

    def __str__(self) -> str:
        return f"{self.group}.{self.name}"

    def run(self, related_visit: RelatedVisitModel = None) -> dict[str, str] | None:
        """Returns a dictionary of {target_model: entry_status, ...} updated
        by running the rule for each target model given a visit.

        Skips run if `appointment.appt_timing` == MISSED_APPT

        Ensure the `model.field` is registered with `site_reference_configs`.
        See `edc_reference`.
        """
        result = None
        if related_visit.appointment.appt_timing != MISSED_APPT:
            result = {}
            opts = {k: v for k, v in self.__dict__.items() if k.startswith != "_"}
            rule_evaluator = self.rule_evaluator_cls(
                related_visit=related_visit, logic=self._logic, **opts
            )
            entry_status = rule_evaluator.result
            for target_model in self.target_models:
                result.update({target_model: entry_status})
        return result
