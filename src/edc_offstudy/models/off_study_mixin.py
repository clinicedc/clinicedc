from django.db import models

from ..constants import OFF_STUDY_REASONS

from .off_study_model_mixin import OffStudyError
from edc_constants.constants import OFF_STUDY


class OffStudyMixin(models.Model):

    """A mixin for scheduled models to add the ability to determine
    if the subject is off study."""

    off_study_model = None

    def save(self, *args, **kwargs):
        self.is_off_study_or_raise()
        super(OffStudyMixin, self).save(*args, **kwargs)

    def is_off_study_or_raise(self):
        """Return True if the off-study report exists or
        a previous visit reason is off study, otherwise False.

        Once consented, a subject must be deliberately taken
        "off study" using a model that uses the
        :class:`edc_off_study.models.OffStudyModelMixin`."""

        subject_identifier = self.get_subject_identifier()
        if not subject_identifier:
            raise ValueError(
                '{} cannot determine the subject identifier. '
                'Got None'.format(self.__class__.__name__))
        try:
            report_datetime = self.report_datetime
        except AttributeError:
            report_datetime = self.get_report_datetime()
        report_date = report_datetime.date()
        off_study = self.has_off_study_report_or_raise(subject_identifier, report_date)
        self.is_off_study_on_previous_visit_or_raise()
        return off_study

    def has_off_study_report_or_raise(self, subject_identifier, report_date):
        """Raises an exception if an off study report exists for this subject with an
        off study date before the report_date."""
        options = {
            '{}__appointment__registered_subject__subject_identifier'.format(self.off_study_model.visit_model_attr):
            subject_identifier}
        try:
            off_study = self.off_study_model.objects.get(
                offstudy_date__lt=report_date,
                **options)
            raise OffStudyError(
                'Participant was reported off study on \'{0}\'. Data reported after this date'
                ' cannot be captured.'.format(off_study.offstudy_date.strftime('%Y-%m-%d')))
        except self.off_study_model.DoesNotExist:
            off_study = None
        return off_study

    def is_off_study_on_previous_visit_or_raise(self):
        """Raise an exception if a previous visit report has a study status off study.

        The visit report is "previous" relative to this objects report_datetime."""
        try:
            previous_off_study_visit = self.off_study_model.visit_model.objects.filter(
                study_status=OFF_STUDY,
                report_datetime__lt=self.report_datetime,
                subject_identifier=self.get_subject_identifier()).order_by('report_datetime')
            if self.visit_model_attr and getattr(self, self.visit_model_attr):
                previous_off_study_visit = previous_off_study_visit.exclude(
                    id=(getattr(self, self.visit_model_attr)).id).last()
            else:
                previous_off_study_visit = previous_off_study_visit.exclude(id=self.id).last()
            if previous_off_study_visit:
                raise OffStudyError(
                    'On a previous visit participant was meant to go off study (reason={}). '
                    'See visit \'{}\' on \'{}\''.format(
                        previous_off_study_visit.reason,
                        previous_off_study_visit.appointment.visit_definition.code,
                        previous_off_study_visit.report_datetime.strftime('%Y-%m-%d')))

        except self.__class__.DoesNotExist:
            pass

    class Meta:
        abstract = True
