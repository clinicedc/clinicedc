from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from edc_base.utils import get_utcnow


class EnrollToScheduleError(Exception):
    pass


class EnrollToSchedule:
    """A class that enrolls a subject to a visit schedule.

    Use `update` to re-create any missing Appointments, for example, when the
    off study model instance is deleted.

    The visit schedule name is taken from the enrollment model
    Meta class option.
    """

    def __init__(self, enrollment_model=None, enrollment_model_cls=None,
                 subject_identifier=None, consent_identifier=None, eligible=None,
                 report_datetime=None):
        self._object = None
        self.enrollment_model_cls = enrollment_model_cls
        self.report_datetime = report_datetime or get_utcnow()
        if not self.enrollment_model_cls:
            self.enrollment_model_cls = django_apps.get_model(enrollment_model)
        self.subject_identifier = subject_identifier
        self.consent_identifier = consent_identifier
        self.eligible = eligible

    def enroll(self):
        """Returns an enrollment model instance by get or create.
        """
        try:
            obj = self.enrollment_model_cls.objects.get(
                subject_identifier=self.subject_identifier)
        except ObjectDoesNotExist:
            self.consented_or_raise()
            obj = self.enrollment_model_cls.objects.create(
                subject_identifier=self.subject_identifier,
                consent_identifier=self.consent_identifier,
                is_eligible=self.eligible,
                report_datetime=self.report_datetime)
        return obj

    def unenroll(self):
        pass

    def update(self):
        """Resaves the enrollment instance to trigger, for example,
        appointment creation (if using edc_appointment mixin).
        """
        obj = self.enrollment_model_cls.objects.get(
            subject_identifier=self.subject_identifier)
        obj.save()

    def consented_or_raise(self):
        """Raises an EnrollToScheduleError exception if one or
        more consents do not exist.
        """
        consent_model_cls = django_apps.get_model(
            self.enrollment_model_cls._meta.consent_model)
        try:
            consent_model_cls.objects.get(
                subject_identifier=self.subject_identifier)
        except ObjectDoesNotExist:
            raise EnrollToScheduleError(
                f'Enrollment failed, consent not found. Using consent model '
                f'\'{self.enrollment_model_cls._meta.consent_model}\' '
                f'subject identifier={self.subject_identifier}.')
        except MultipleObjectsReturned:
            pass
