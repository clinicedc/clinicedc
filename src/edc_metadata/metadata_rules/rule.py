from __future__ import annotations

import contextlib
from collections.abc import Callable
from datetime import datetime
from typing import TYPE_CHECKING

from django.utils import timezone

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
        predicate: P | PF | Callable | str,
        consequence: str,
        alternative: str,
        *,
        activate_until_datetime: datetime | None = None,
        activate_after_datetime: datetime | None = None,
        disable_until_datetime: datetime | None = None,
        disable_after_datetime: datetime | None = None,
    ) -> None:
        self.predicate = predicate
        self.consequence = consequence
        self.alternative = alternative

        self.target_models: list[str] = []

        self.activate_until_datetime = activate_until_datetime
        self.activate_after_datetime = activate_after_datetime
        self.disable_until_datetime = disable_until_datetime
        self.disable_after_datetime = disable_after_datetime
        self.validate_run_and_disable_datetimes()

        self.app_label: str | None = None  # set by metaclass
        self.group = None  # set by metaclass
        self.name: str | None = None  # set by metaclass
        self.source_model: str | None = None  # set by metaclass
        self.related_visit_model: str | None = None  # set by metaclass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', group='{self.group}')"

    def __str__(self) -> str:
        return f"{self.group}.{self.name}"

    def run(self, related_visit: RelatedVisitModel) -> dict[str, str] | None:
        """Returns a dictionary of {target_model: entry_status, ...} updated
        by running the rule for each target model given a visit.

        Skips run if `appointment.appt_timing` == MISSED_APPT
        """
        result = {}

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

        if related_visit.appointment.appt_timing != MISSED_APPT and not self.is_disabled(
            related_visit
        ):
            result = {}
            entry_status = self.get_entry_status(related_visit)
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

    def get_entry_status(self, related_visit):
        opts = {k: v for k, v in self.__dict__.items() if k.startswith != "_"}
        rule_evaluator = self.rule_evaluator_cls(
            related_visit=related_visit, logic=self.logic, **opts
        )
        if (
            self.activate_after_datetime or self.activate_until_datetime
        ) and not self.within_a_run_only_datetime_boundary(related_visit):
            entry_status = self.alternative
        else:
            entry_status = rule_evaluator.result
        return entry_status

    def is_disabled(self, related_visit) -> bool:
        dt = related_visit.report_datetime
        return (
            self.disable_after_datetime is not None and dt > self.disable_after_datetime
        ) or (self.disable_until_datetime is not None and dt < self.disable_until_datetime)

    def within_a_run_only_datetime_boundary(self, related_visit) -> bool:
        """Return True if the visit datetime falls within every
        `activate` boundary that is set.

        Only called where at least one `activate` datetime is set. Where
        both are set the boundary is the range between them, so the
        visit datetime must satisfy both, not either.
        """
        dt = related_visit.report_datetime
        after = self.activate_after_datetime
        until = self.activate_until_datetime
        return (after is None or dt > after) and (until is None or dt < until)

    def validate_run_and_disable_datetimes(self):
        if self.activate_after_datetime and timezone.is_naive(self.activate_after_datetime):
            raise RuleError("activate_after_datetime must be timezone-aware")
        if self.activate_until_datetime and timezone.is_naive(self.activate_until_datetime):
            raise RuleError("activate_until_datetime must be timezone-aware")
        if self.disable_after_datetime and timezone.is_naive(self.disable_after_datetime):
            raise RuleError("disable_after_datetime must be timezone-aware")
        if self.disable_until_datetime and timezone.is_naive(self.disable_until_datetime):
            raise RuleError("disable_until_datetime must be timezone-aware")
        if (
            self.activate_after_datetime
            and self.activate_until_datetime
            and self.activate_after_datetime > self.activate_until_datetime
        ):
            raise RuleError("activate_after_datetime is after activate_until_datetime")
        if (
            self.disable_after_datetime
            and self.disable_until_datetime
            and self.disable_after_datetime > self.disable_until_datetime
        ):
            raise RuleError("disable_after_datetime is after disable_until_datetime")
