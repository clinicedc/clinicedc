from edc_visit_schedule.site_visit_schedules import site_visit_schedules


class EnrolledSubject:

    def __init__(self, subject_identifier=None, **kwargs):
        self.subject_identifier = subject_identifier

    def enrollments(self, visit_schedule_name=None, schedule_name=None, **kwargs):
        """Returns a list of the subjects enrollment instances.

        options: query options for the enrollment model.
        """
        enrollments = []
        for visit_schedule in site_visit_schedules.get_visit_schedules(
                visit_schedule_name=visit_schedule_name).values():
            for schedule in visit_schedule.get_schedules(schedule_name=schedule_name).values():
                try:
                    enrollments.append(schedule.enrollment_model.objects.get(
                        subject_identifier=self.subject_identifier,
                        visit_schedule_name=visit_schedule.name,
                        schedule_name=schedule.name))
                except schedule.enrollment_model.DoesNotExist:
                    pass
        return enrollments

    def enrollment(self, subject_identifier=None, visit_schedule_name=None, schedule_name=None, **kwargs):
        """Returns the enrollment instance for the given subject.
        """
        visit_schedule = self.get_visit_schedule(
            visit_schedule_name=visit_schedule_name)
        schedule = visit_schedule.get_schedule(schedule_name=schedule_name)
        model = schedule.enrollment_model
        try:
            obj = model.objects.get(
                subject_identifier=subject_identifier)
        except model.DoesNotExist:
            obj = None
        return obj

    def last_visit_datetime(self, subject_identifier,
                            visit_schedule_name=None, schedule_name=None):
        """Returns the last visit datetime for a subject.

        Does not assume every visit schedule uses the same visit model.
        """
        last_visit_datetime = None
        if schedule_name and not visit_schedule_name:
            raise TypeError(
                'Specify \'visit_schedule_name\' when specifying '
                '\'schedule_name\'. Got None')
        schedule_names = [] if not schedule_name else [schedule_name]
        visit_models = []
        max_visit_datetimes = []
        visit_schedule_names = ([
            visit_schedule_name]
            if visit_schedule_name else self.get_visit_schedule_names())
        if not schedule_names:
            for visit_schedule_name in visit_schedule_names:
                schedule_names.extend(
                    self.get_schedule_names(visit_schedule_name))
        for visit_schedule in [
                v for k, v in self.registry.items() if k in visit_schedule_names]:
            schedule_names = self.get_schedule_names(visit_schedule.name)
            if visit_schedule.visit_model not in visit_models:
                visit_models.append(visit_schedule.visit_model)
                last_visit = visit_schedule.visit_model.objects.last_visit(
                    subject_identifier=subject_identifier,
                    visit_schedule_names=visit_schedule_names,
                    schedule_names=schedule_names)
                if last_visit:
                    max_visit_datetimes.append(last_visit.report_datetime)
        if max_visit_datetimes:
            last_visit_datetime = max(max_visit_datetimes)
        return last_visit_datetime
