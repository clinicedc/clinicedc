from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.base import ContextMixin

from .site_visit_schedules import site_visit_schedules


class VisitScheduleViewMixin(ContextMixin):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.onschedule_models = []
        self.current_onschedule_model = None
        self.schedule = None
        self.visit_schedules = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        for visit_schedule in site_visit_schedules.visit_schedules.values():
            for schedule in visit_schedule.schedules.values():
                try:
                    onschedule_instance = schedule.onschedule_model_cls.objects.get(
                        subject_identifier=self.subject_identifier)
                except ObjectDoesNotExist:
                    pass
                else:
                    self.visit_schedules.append(visit_schedule)
                    if self.is_current_onschedule_model(
                            onschedule_instance, schedule=schedule):
                        onschedule_instance.current = True
                        self.current_onschedule_model = onschedule_instance
                    self.onschedule_models.append(onschedule_instance)

        context.update(
            visit_schedules=self.visit_schedules,
            onschedule_models=self.onschedule_models,
            current_onschedule_model=self.current_onschedule_model)
        return context

    def is_current_onschedule_model(self, onschedule_instance,
                                    visit_schedule=None, **kwargs):
        """Returns True if instance is the current onschedule model.

        Override to set the criteria of what is "current"
        """
        return False
