from django.utils import timezone
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from .enrolled_subject import EnrolledSubject


class DisenrollmentError(Exception):
    pass


class DisenrollmentValidator:

    """A class to validate that to disenroll is valid.
    """

    def __init__(self, subject_identifier=None, disenrollment_datetime=None,
                 visit_schedule_name=None, schedule_name=None):
        self.disenrollment_datetime = disenrollment_datetime
        self.schedule_name = schedule_name
        self.subject_identifier = subject_identifier
        self.visit_schedule_name = visit_schedule_name
        self.validate()

    def validate(self):
        visit_schedule = site_visit_schedules.get_visit_schedule(
            visit_schedule_name=self.visit_schedule_name)
        schedule = visit_schedule.get_schedule(
            schedule_name=self.schedule_name)

        try:
            enrollment = schedule.enrollment_model_cls.objects.get(
                subject_identifier=self.subject_identifier)
        except schedule.enrollment_model_cls.DoesNotExist as e:
            raise DisenrollmentError(
                f'Cannot disenroll before enrollment. Subject \'{self.subject_identifier}\' '
                f'is not enrolled to \'{self.visit_schedule_name}.{self.schedule_name}\'. '
                f'Got {e}') from e

        tdelta = enrollment.report_datetime - self.disenrollment_datetime
        if tdelta.days > 0:
            raise DisenrollmentError(
                f'Disenrollment datetime cannot precede the enrollment '
                f'datetime {timezone.localtime(enrollment.report_datetime)}. '
                f'Got {timezone.localtime(self.disenrollment_datetime)}')

        enrolled_subject = EnrolledSubject(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule_name,
            schedule_name=self.schedule_name)
        try:
            last_visit = enrolled_subject.visits[-1:][0]
        except IndexError:
            pass
        else:
            tdelta = last_visit.report_datetime - self.disenrollment_datetime
            if tdelta.days > 0:
                raise DisenrollmentError(
                    f'Disenrollment datetime cannot precede the last visit '
                    f'datetime {timezone.localtime(last_visit.report_datetime)}. '
                    f'Got {timezone.localtime(self.disenrollment_datetime)}')
