from edc_visit_schedule.site_visit_schedules import site_visit_schedules


class EnrolledSubject:

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
            schedules = site_visit_schedules.get_schedules(
                visit_schedule_name=visit_schedule.name,
                schedule_name=schedule_name)
            for schedule in schedules.values():
                try:
                    obj = schedule.enrollment_model.objects.get(
                        subject_identifier=self.subject_identifier)
                except schedule.enrollment_model.DoesNotExist:
                    pass
                else:
                    self.enrollments.append(obj)
                    self.visit_schedules.update(
                        {visit_schedule.name: visit_schedule})
                    self.schedules.update({schedule.name: schedule})
                    visit_model = visit_schedule.models.get('visit_model')
                    try:
                        self.visits.append(visit_model.objects.get(
                            subject_identifier=self.subject_identifier))
                    except visit_model.DoesNotExist:
                        pass
        self.visits.sort(key=lambda x: x.report_datetime)
        self.enrollments.sort(key=lambda x: x.report_datetime)
