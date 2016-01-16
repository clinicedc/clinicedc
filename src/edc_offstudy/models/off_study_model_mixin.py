from datetime import datetime, time

from django.db import models

from edc_base.encrypted_fields import mask_encrypted
from edc_base.model.fields import OtherCharField
from edc_base.model.validators.date import date_not_before_study_start, date_not_future

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

    def __unicode__(self):
        return "{0} {1} ({2})".format(
            self.registered_subject.subject_identifier,
            self.registered_subject.subject_type,
            mask_encrypted(self.registered_subject.first_name))

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
