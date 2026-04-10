from __future__ import annotations

from datetime import datetime
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
        run_only_after_datetime: datetime | None = None,
        run_only_for_visit_schedules: list[str] | None = None,
        **kwargs,
    ) -> None:
        """Note: run_only_for_visit_schedules format is
        [visit_schedule.schedule, ...]
        """
        super().__init__(**kwargs)
        self.metadata_category = CRF
        self.target_models = target_models
        self.run_only_after_datetime = run_only_after_datetime
        self.run_only_for_visit_schedules = run_only_for_visit_schedules or []

    def run(self, related_visit: RelatedVisitModel = None) -> dict[str, str] | None:
        visit_schedule_schedule = f"{related_visit.visit_schedule}.{related_visit.schedule}"
        if self.source_model in self.target_models:
            raise CrfRuleModelConflict(
                f"Source model cannot be a target model. Got '{self.source_model}' "
                f"is in target models {self.target_models}"
            )
        if (
            self.run_only_for_visit_schedules
            and visit_schedule_schedule not in self.run_only_for_visit_schedules
        ) or (
            self.run_only_after_datetime
            and related_visit.report_datetime < self.run_only_after_datetime
        ):
            return None
        return super().run(related_visit=related_visit)
