from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

from edc_appointment.constants import MISSED_APPT

from .logic import Logic
from .rule_evaluator import RuleEvaluator

if TYPE_CHECKING:
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
        predicate: P | PF | callable | str = None,
        consequence: str = None,
        alternative: str = None,
    ) -> None:
        self.predicate = predicate
        self.consequence = consequence
        self.alternative = alternative
        self.target_models: list[str] | None = None
        self.app_label: str | None = None  # set by metaclass
        self.group = None  # set by metaclass
        self.name: str | None = None  # set by metaclass
        self.source_model: str | None = None  # set by metaclass
        self.related_visit_model: str | None = None  # set by metaclass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', group='{self.group}')"

    def __str__(self) -> str:
        return f"{self.group}.{self.name}"

    def run(self, related_visit: RelatedVisitModel = None) -> dict[str, str] | None:
        """Returns a dictionary of {target_model: entry_status, ...} updated
        by running the rule for each target model given a visit.

        Skips run if `appointment.appt_timing` == MISSED_APPT
        """
        result = None
        if (
            self.related_visit_model
            and self.related_visit_model != related_visit._meta.label_lower
        ):
            raise RuleError(
                "Conflicting related visit model on rule. "
                f"Got {self.related_visit_model} != {related_visit._meta.label_lower}."
                "Try specifying the related visit model on RuleGroup.Meta explicitly. "
                f'For example, related_visit_model = "{related_visit._meta.label_lower}" '
                f"See {self}. "
            )

        if related_visit.appointment.appt_timing != MISSED_APPT:
            result = {}
            opts = {k: v for k, v in self.__dict__.items() if k.startswith != "_"}
            rule_evaluator = self.rule_evaluator_cls(
                related_visit=related_visit, logic=self.logic, **opts
            )
            entry_status = rule_evaluator.result
            for target_model in self.target_models:
                result.update({target_model: entry_status})
        return result

    @property
    def logic(self) -> Logic:
        return self.logic_cls(
            predicate=self.predicate,
            consequence=self.consequence,
            alternative=self.alternative,
        )

    @property
    def field_names(self) -> list[str]:
        field_names = []
        try:
            field_names = [self.predicate.attr]
        except AttributeError:
            with contextlib.suppress(AttributeError):
                field_names = self.predicate.attrs
        return field_names
