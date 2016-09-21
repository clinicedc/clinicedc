from datetime import datetime, time
from django.db import models

from edc_base.model.fields import OtherCharField
from edc_base.model.validators.date import date_not_future
from edc_protocol.validators import date_not_before_study_start
from edc_constants.constants import OFF_STUDY


class OffStudyError(Exception):
    pass


class OffStudyModelManager(models.Manager):
    """A manager class for Crf models, models that have an FK to the visit tracking model."""

    def get_by_natural_key(self, visit_instance_number, code, subject_identifier_as_pk):
        instance = self.model.visit_model.objects.get_by_natural_key(
            visit_instance_number, code, subject_identifier_as_pk)
        return self.get({self.model.visit_model_attr: instance})


class OffStudyModelMixin(models.Model):
    """Mixin for the Off Study model.

    OffStudyModel is a CRF model!

    You need to add a foreign key to your visit model

        subject_visit = models.OneToOneField(SubjectVisit)

    """

    offstudy_date = models.DateField(
        verbose_name="Off-study Date",
        validators=[
            date_not_before_study_start,
            date_not_future])

    reason = models.CharField(
        verbose_name="Please code the primary reason participant taken off-study",
        max_length=115)

    reason_other = OtherCharField()

    comment = models.TextField(
        max_length=250,
        verbose_name="Comment",
        blank=True,
        null=True)

    objects = OffStudyModelManager()

    def natural_key(self):
        return (self.offstudy_date, ) + self.registered_subject.natural_key()

    def __str__(self):
        return "{0} {1} ({2})".format(
            self.registered_subject.subject_identifier)

    def save(self, *args, **kwargs):
        self.off_study_visit_exists_or_raise()
        super(OffStudyModelMixin, self).save(*args, **kwargs)

    @property
    def registered_subject(self):
        return getattr(self, self.visit_model_attr).appointment.registered_subject

    def off_study_visit_exists_or_raise(self, exception_cls=None):
        """Confirms the off study report datetime matches a off study visit report datetime
        or raise an OffStudyError."""
        exception_cls = exception_cls or OffStudyError
        report_datetime_min = datetime.combine(self.report_datetime.date(), time.min)
        report_datetime_max = datetime.combine(self.report_datetime.date(), time.max)
        try:
            self.visit_model.objects.get(
                appointment__registered_subject=self.registered_subject,
                report_datetime__gte=report_datetime_min,
                report_datetime__lte=report_datetime_max,
                study_status=OFF_STUDY)
        except self.visit_model.DoesNotExist:
            raise exception_cls(
                'Off study report must be submitted with a visit report on the '
                'same day with study_status set to \'off study\'. '
                'Using off study report date {}.'.format(self.report_datetime.date()))

    def delete_future_appointments_on_offstudy(self):
        """Deletes appointments created after the off-study datetime
        if the appointment has no visit report."""
        Appointment = self.visit_model.appointment.field.rel.to
        for appointment in Appointment.objects.filter(
                registered_subject=self.registered_subject,
                appt_datetime__gt=self.offstudy_date):
            # only delete appointments that have no visit report
            try:
                self.visit_model.objects.get(appointment=appointment)
            except self.visit_model.DoesNotExist:
                appointment.delete()

    def get_subject_identifier(self):
        return self.registered_subject.subject_identifier

    def get_report_datetime(self):
        return self.report_datetime

    class Meta:
        abstract = True


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
