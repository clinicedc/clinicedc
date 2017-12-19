from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.base import ContextMixin

from .site_visit_schedules import site_visit_schedules


class VisitScheduleViewMixin(ContextMixin):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.enrollment_models = []
        self.current_enrollment_model = None
        self.schedule = None
        self.visit_schedules = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        for visit_schedule in site_visit_schedules.visit_schedules.values():
            for schedule in visit_schedule.schedules.values():
                try:
                    enrollment_instance = schedule.enrollment_model_cls.objects.get(
                        subject_identifier=self.subject_identifier)
                except ObjectDoesNotExist:
                    pass
                else:
                    self.visit_schedules.append(visit_schedule)
                    if self.is_current_enrollment_model(
                            enrollment_instance, schedule=schedule):
                        enrollment_instance.current = True
                        self.current_enrollment_model = enrollment_instance
                    self.enrollment_models.append(enrollment_instance)

        context.update(
            visit_schedules=self.visit_schedules,
            enrollment_models=self.enrollment_models,
            current_enrollment_model=self.current_enrollment_model)
        return context

    def is_current_enrollment_model(self, enrollment_instance,
                                    visit_schedule=None, **kwargs):
        """Returns True if instance is the current enrollment model.

        Override to set the criteria of what is "current"
        """
        return False
