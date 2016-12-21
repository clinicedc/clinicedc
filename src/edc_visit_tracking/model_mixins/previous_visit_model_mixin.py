from django.db import models, transaction


class PreviousVisitError(Exception):
    pass


class PreviousVisitModelMixin(models.Model):

    """A model mixin to force the user to complete visit model instances in sequence.

    * Ensures the previous visit exists before allowing save() by raising PreviousVisitError.
    * If the visit is the first in the sequence, save() is allowed.
    * If 'requires_previous_visit' = False, mixin is disabled.

    Important: Use together with the VisitModelMixin. Requires methods from the VisitModelMixin

    """

    requires_previous_visit = True

    def save(self, *args, **kwargs):
        self.has_previous_visit_or_raise()
        super(PreviousVisitModelMixin, self).save(*args, **kwargs)

    def has_previous_visit_or_raise(self, exception_cls=None):
        """Returns True if the previous visit in the schedule exists or this is the first visit.

        Is by-passed if 'requires_previous_visit' is False.

        You can call this from the forms clean() method."""
        exception_cls = exception_cls or PreviousVisitError
        if self.requires_previous_visit and self.previous_visit_code:
            if self.previous_visit:
                has_previous_visit = True
            elif (self.appointment.timepoint == 0 and self.appointment.base_interval == 0):
                has_previous_visit = True
            else:
                has_previous_visit = False
            if not has_previous_visit:
                raise exception_cls({
                    'appointment':
                    'Previous visit report required. Enter report for \'{}\' before completing this report.'.format(
                        self.previous_visit_code)})

    @property
    def previous_visit_code(self):
        try:
            previous_visit_code = self.schedule.get_previous_visit(self.visit_code).code
        except AttributeError:
            previous_visit_code = None
        return previous_visit_code

    @property
    def previous_visit(self):
        """Returns the previous visit model instance if it exists."""
        previous_visit = None
        if self.previous_visit_code:
            with transaction.atomic():
                try:
                    previous_visit = self.__class__.objects.get(
                        appointment__subject_identifier=self.appointment.subject_identifier,
                        visit_schedule_name=self.visit_schedule_name,
                        schedule_name=self.schedule_name,
                        visit_code=self.previous_visit_code)
                except self.__class__.DoesNotExist:
                    previous_visit = None
                except self.__class__.MultipleObjectsReturned:
                    previous_appointment = self.appointment.__class__.objects.filter(
                        subject_identifier=self.appointment.subject_identifier,
                        visit_code=self.previous_visit_code).order_by('-visit_instance')[0]
                    previous_visit = self.__class__.objects.get(
                        appointment=previous_appointment)
        return previous_visit

    class Meta:
        abstract = True
