from django.db import models, transaction

from edc.subject.visit_schedule.models.visit_definition import VisitDefinition


class PreviousVisitError(Exception):
    pass


class PreviousVisitMixin(models.Model):

    """A mixin to force the user to complete visits in sequence.

    * Ensures the previous visit exists before allowing save() by raising PreviousVisitError.
    * If the visit is the first in the sequence, save() is allowed.
    * If REQUIRES_PREVIOUS_VISIT = False, mixin is disabled.

    ...note: Review the value of \'time_point\' and \'base_interval\' from VisitDefintion
        to confirm the visits are in order. This mixin assumes ordering VisitDefinition
        by 'time_point' and 'base_interval' gives the correct visit code sequence.
        Also assumes visits are grouped by the visit tracking form and the \'group\' attr.

    For example:

        class TestVisit(MetaDataMixin, PreviousVisitMixin, BaseVisitTracking):

            REQUIRES_PREVIOUS_VISIT = True

            def custom_post_update_entry_meta_data(self):
                pass

            class Meta:
                app_label = 'my_app'

    """

    REQUIRES_PREVIOUS_VISIT = True

    def save(self, *args, **kwargs):
        self.has_previous_visit_or_raise()
        super(PreviousVisitMixin, self).save(*args, **kwargs)

    def has_previous_visit_or_raise(self, exception_cls=None):
        """Returns True if the previous visit in the schedule exists or this is the first visit.

        Is by-passed if REQUIRES_PREVIOUS_VISIT is False.

        You can call this from the forms clean() method."""
        exception_cls = exception_cls or PreviousVisitError
        if self.REQUIRES_PREVIOUS_VISIT:
            previous_visit_definition = self.previous_visit_definition(
                self.appointment.visit_definition)
            if previous_visit_definition:
                if self.previous_visit(previous_visit_definition):
                    has_previous_visit = True
                elif (self.appointment.visit_definition.time_point == 0 and
                        self.appointment.visit_definition.base_interval == 0):
                    has_previous_visit = True
                else:
                    has_previous_visit = False
                if not has_previous_visit:
                    raise exception_cls(
                        'Previous visit report for \'{}\' is not complete.'.format(previous_visit_definition.code))

    def previous_visit_definition(self, visit_definition):
        """Returns the previous visit definition relative to this instance or None.

        Only selects visit definition instances for this visit model."""
        previous_visit_definition = VisitDefinition.objects.filter(
            time_point__lt=visit_definition.time_point,
            visit_tracking_content_type_map__app_label=self._meta.app_label,
            visit_tracking_content_type_map__module_name=self._meta.model_name,
            grouping=visit_definition.grouping).order_by(
                'time_point', 'base_interval').last()
        if previous_visit_definition:
            return previous_visit_definition
        return None

    def previous_visit(self, previous_visit_definition=None):
        """Returns the previous visit if it exists."""
        with transaction.atomic():
            try:
                previous_visit_definition = previous_visit_definition or self.previous_visit_definition(
                    self.appointment.visit_definition)
                previous_visit = self.__class__.objects.get(
                    appointment__visit_definition=previous_visit_definition)
            except self.__class__.DoesNotExist:
                previous_visit = None
        return previous_visit

    class Meta:
        abstract = True
