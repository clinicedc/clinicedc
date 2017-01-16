from edc_visit_schedule.site_visit_schedules import site_visit_schedules


class VisitScheduleViewMixin:

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.visit_schedules = []
        self.enromment_models = []
        self.schedule = None

    def get(self, request, *args, **kwargs):
        visit_schedules = site_visit_schedules.get_visit_schedules().values()
        # find if the subject has an enrollment for for a schedule
        for visit_schedule in visit_schedules:
            for schedule in visit_schedule.schedules.values():
                enrollment_instance = schedule.enrollment_instance(
                    subject_identifier=self.subject_identifier)
                if enrollment_instance:
                    self.visit_schedules.append(visit_schedule)
                    self.enromment_models.append(enrollment_instance)
                    break
        kwargs['visit_schedules'] = self.visit_schedules
        kwargs['enromment_models'] = self.enromment_models
        return super().get(request, *args, **kwargs)
