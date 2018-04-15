from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import transaction


class VisitSequenceError(Exception):
    pass


class VisitSequence:

    """A class that calculates the previous_visit and can enforce
    that the sequence of visits are completed in order.
    """

    def __init__(self, appointment=None):
        self.appointment = appointment
        self.appointment_model_cls = self.appointment.__class__
        self.model_cls = getattr(
            self.appointment_model_cls,
            self.appointment_model_cls.related_visit_model_attr()
        ).related.related_model
        self.subject_identifier = self.appointment.subject_identifier
        self.visit_schedule_name = self.appointment.visit_schedule_name
        self.visit_code = self.appointment.visit_code
        previous_visit = self.appointment.schedule.visits.previous(
            self.visit_code)
        try:
            self.previous_visit_code = previous_visit.code
        except AttributeError:
            self.previous_visit_code = None
        self.previous_visit_missing = self.previous_visit_code and not self.previous_visit

    def enforce_sequence(self):
        """Raises an exception if sequence is not adhered to; that is,
        the visits are not completed in order.
        """
        if self.previous_visit_missing:
            raise VisitSequenceError(
                'Previous visit report required. Enter report for '
                f'\'{self.previous_visit_code}\' before completing this report.')

    @property
    def previous_visit(self):
        """Returns the previous visit model instance if it exists.
        """
        previous_visit = None
        if self.previous_visit_code:
            with transaction.atomic():
                try:
                    previous_visit = self.model_cls.objects.get(
                        appointment__subject_identifier=self.subject_identifier,
                        visit_schedule_name=self.visit_schedule_name,
                        schedule_name=self.appointment.schedule_name,
                        visit_code=self.previous_visit_code)
                except ObjectDoesNotExist:
                    previous_visit = None
                except MultipleObjectsReturned:
                    previous_appointment = self.appointment_model_cls.objects.filter(
                        subject_identifier=self.subject_identifier,
                        visit_code=self.previous_visit_code).order_by(
                            '-visit_code_sequence')[0]
                    previous_visit = self.model_cls.objects.get(
                        appointment=previous_appointment)
        return previous_visit
