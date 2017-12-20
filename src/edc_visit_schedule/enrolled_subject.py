from django.core.exceptions import ObjectDoesNotExist

from .site_visit_schedules import site_visit_schedules


class EnrolledSubject:

    """A class that collects all the enrollment model instances
    for an enrolled subject.

    See `enrollments`
    """

    def __init__(self, subject_identifier=None, visit_schedule_name=None,
                 schedule_name=None, **kwargs):
        self.enrollments = []
        self.visits = []
        self.visit_schedules = {}
        self.schedules = {}
        self.subject_identifier = subject_identifier

        visit_schedules = site_visit_schedules.get_visit_schedules(
            visit_schedule_name=visit_schedule_name)

        for visit_schedule in visit_schedules.values():
            if schedule_name:
                schedules = {
                    k: v for k, v in visit_schedule.schedules.items()
                    if k == schedule_name}
            else:
                schedules = visit_schedule.schedules
            for schedule in schedules.values():
                try:
                    obj = schedule.enrollment_model_cls.objects.get(
                        subject_identifier=self.subject_identifier)
                except ObjectDoesNotExist:
                    pass
                else:
                    self.enrollments.append(obj)
                    self.visit_schedules.update(
                        {visit_schedule.name: visit_schedule})
                    self.schedules.update({schedule.name: schedule})
                    try:
                        visit = visit_schedule.visit_model_cls.objects.get(
                            subject_identifier=self.subject_identifier)
                    except ObjectDoesNotExist:
                        pass
                    else:
                        self.visits.append(visit)
        self.visits.sort(key=lambda x: x.report_datetime)
        self.enrollments.sort(key=lambda x: x.report_datetime)
