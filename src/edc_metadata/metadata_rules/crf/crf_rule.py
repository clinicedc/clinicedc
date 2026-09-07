from __future__ import annotations

from typing import TYPE_CHECKING

from ...constants import CRF
from ..rule import Rule

if TYPE_CHECKING:
    from edc_visit_tracking.model_mixins import VisitModelMixin as Base

    from ...model_mixins.creates import CreatesMetadataModelMixin

    class RelatedVisitModel(CreatesMetadataModelMixin, Base):
        pass


class CrfRuleModelConflict(Exception):  # noqa: N818
    pass


class CrfRule(Rule):
    def __init__(
        self,
        target_models: list[str],
        run_only_for_visit_schedules: list[str] | None = None,
        run_only_for_visit_codes: list[str] | None = None,
        **kwargs,
    ) -> None:
        """Note: run_only_for_visit_schedules format is
        [visit_schedule.schedule, ...]
        """
        super().__init__(**kwargs)
        self.metadata_category = CRF
        self.target_models: list[str] = target_models
        self.run_only_for_visit_schedules = run_only_for_visit_schedules or []
        self.run_only_for_visit_codes = run_only_for_visit_codes or []

    def run_is_applicable(self, related_visit) -> bool:
        """Evaluate run_only datetimes, if set, against the related
        visit datetime.

        * If run_only datetimes are NOT set, return True
        * If run_only datetimes are set and the visit datetime is
          within the datetime boundary, return True.
        * If run_only datetimes are set and the visit datetime is
          NOT within the datetime boundary, return False.
        """
        visit_schedule_schedule = f"{related_visit.visit_schedule}.{related_visit.schedule}"
        if (
            self.run_only_for_visit_schedules
            and visit_schedule_schedule not in self.run_only_for_visit_schedules
        ):
            return False

        if (  # noqa: SIM103
            self.run_only_for_visit_codes
            and related_visit.visit_code not in self.run_only_for_visit_codes
        ):
            return False
        return True

    def run(self, related_visit: RelatedVisitModel) -> dict[str, str] | None:
        if self.source_model in self.target_models:
            raise CrfRuleModelConflict(
                f"Source model cannot be a target model. Got '{self.source_model}' "
                f"is in target models {self.target_models}"
            )
        if self.run_is_applicable(related_visit):
            return super().run(related_visit=related_visit)
        return None
