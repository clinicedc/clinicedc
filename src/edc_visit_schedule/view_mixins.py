from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.base import ContextMixin
from edc_utils import get_utcnow

from .site_visit_schedules import site_visit_schedules


class VisitScheduleViewMixin(ContextMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.onschedule_models = []
        self.current_schedule = None
        self.current_visit_schedule = None
        self.current_onschedule_model = None
        self.visit_schedules = {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for visit_schedule in site_visit_schedules.visit_schedules.values():
            for schedule in visit_schedule.schedules.values():
                if not self.current_schedule:
                    self.current_schedule = schedule
                    self.current_visit_schedule = visit_schedule
                try:
                    onschedule_model_obj = schedule.onschedule_model_cls.objects.get(
                        subject_identifier=self.subject_identifier
                    )
                except ObjectDoesNotExist:
                    pass
                else:
                    if schedule.is_onschedule(
                        subject_identifier=self.kwargs.get("subject_identifier"),
                        report_datetime=get_utcnow(),
                    ):
                        self.current_schedule = schedule
                        self.current_visit_schedule = visit_schedule
                        self.current_onschedule_model = onschedule_model_obj
                    self.onschedule_models.append(onschedule_model_obj)
                    self.visit_schedules.update({visit_schedule.name: visit_schedule})

        context.update(
            visit_schedules=self.visit_schedules,
            current_onschedule_model=self.current_onschedule_model,
            onschedule_models=self.onschedule_models,
            current_schedule=self.current_schedule,
            current_visit_schedule=self.current_visit_schedule,
        )
        return context
