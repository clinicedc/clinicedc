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
        # force create of enrollment model instance
        self.object

    @property
    def object(self):
        if not self._object:
            try:
                self._object = self.enrollment_model_cls.objects.get(
                    subject_identifier=self.subject_identifier,
                    visit_schedule_name=self.enrollment_model_cls._meta.visit_schedule_name)
            except ObjectDoesNotExist:
                self.consented_or_raise()
                self._object = self.enrollment_model_cls.objects.create(
                    subject_identifier=self.subject_identifier,
                    consent_identifier=self.consent_identifier,
                    is_eligible=self.eligible,
                    report_datetime=self.report_datetime,
                    visit_schedule_name=self.enrollment_model_cls._meta.visit_schedule_name)
        return self._object

    def update(self):
        self.object.save()

    def consented_or_raise(self):
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
