from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from .site_visit_schedules import site_visit_schedules

if TYPE_CHECKING:
    from .model_mixins import OnScheduleModelMixin
    from .schedule import Schedule
    from .visit_schedule import VisitSchedule

    class OnScheduleLikeModel(OnScheduleModelMixin): ...


class VisitScheduleViewMixin:
    def __init__(self, **kwargs):
        self.onschedule_models: list[OnScheduleLikeModel] = []
        self.current_schedule: Schedule | None = None
        self.current_visit_schedule: VisitSchedule | None = None
        self.current_onschedule_model: str | None = None
        self.visit_schedules: dict[str, VisitSchedule] = {}
        super().__init__(**kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        # TODO: What if active on more than one schedule??
        for visit_schedule in site_visit_schedules.visit_schedules.values():
            if self.subject_identifier:
                for schedule in visit_schedule.schedules.values():
                    try:
                        onschedule_model_obj = schedule.onschedule_model_cls.objects.get(
                            subject_identifier=self.subject_identifier
                        )
                    except ObjectDoesNotExist:
                        pass
                    else:
                        self.onschedule_models.append(onschedule_model_obj)
                        self.visit_schedules.update({visit_schedule.name: visit_schedule})
                        if schedule.is_onschedule(self.subject_identifier, timezone.now()):
                            self.current_schedule = schedule
                            self.current_visit_schedule = visit_schedule
                            self.current_onschedule_model = onschedule_model_obj

        kwargs.update(
            visit_schedules=self.visit_schedules,
            current_onschedule_model=self.current_onschedule_model,
            onschedule_models=self.onschedule_models,
            current_schedule=self.current_schedule,
            current_visit_schedule=self.current_visit_schedule,
        )
        return super().get_context_data(**kwargs)
