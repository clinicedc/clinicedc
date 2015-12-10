from datetime import datetime, date, time

from django.db import models
from django.db.models import Max

from edc_constants.choices import YES_NO
from edc_constants.constants import YES, NO, OFF_STUDY
from edc_base.encrypted_fields import mask_encrypted
from edc_base.model.fields import OtherCharField
from edc.base.model.validators.date import datetime_not_before_study_start, datetime_not_future


class OffStudyError(Exception):
    pass


class OffStudyModelMixin(models.Model):
    """Mixin for the Off Study model."""

    VISIT_MODEL = None
    # registered_subject = models.OneToOneField(RegisteredSubject)

    report_datetime = models.DateTimeField(
        verbose_name="Visit Date and Time",
        validators=[
            datetime_not_before_study_start,
            datetime_not_future],
        help_text='Date and time of this report'
    )

    offstudy_date = models.DateField(
        verbose_name="Off-study Date",
        validators=[
            datetime_not_before_study_start,
            datetime_not_future])

    reason = models.CharField(
        verbose_name="Please code the primary reason participant taken off-study",
        max_length=115)

    reason_other = OtherCharField()

    has_scheduled_data = models.CharField(
        max_length=10,
        verbose_name='Are scheduled data being submitted on the off-study date?',
        choices=YES_NO,
        default=YES,
        help_text='')

    comment = models.TextField(
        max_length=250,
        verbose_name="Comment",
        blank=True,
        null=True)

#     objects = OffStudyManager()
#
#     def natural_key(self):
#         return (self.offstudy_date, ) + self.registered_subject.natural_key()

    def __unicode__(self):
        return "{0} {1} ({2})".format(self.registered_subject.subject_identifier,
                                      self.registered_subject.subject_type,
                                      mask_encrypted(self.registered_subject.first_name))

    def save(self, *args, **kwargs):
        self.off_study_visit_exists_or_raise()
        super(OffStudyModelMixin, self).save(*args, **kwargs)

    def show_scheduled_entries_on_offstudy_date(self):
        if self.has_scheduled_data == NO:
            return False
        return True

    def get_subject_identifier(self):
        return self.registered_subject.subject_identifier

#     def offstudy_date_or_raise(self, exception_cls=None):
#         """Checks that off study date is on or after the visit model visit_datetime."""
#         exception_cls = exception_cls or OffStudyError
#         aggregate = self.VISIT_MODEL.objects.filter(
#             appointment__registered_subject=self.registered_subject).aggregate(
#                 Max('report_datetime'))
#         max_report_datetime = aggregate.get('report_datetime__max')
#         if max_report_datetime:
#             report_date = date(max_report_datetime.year,
#                                max_report_datetime.month,
#                                max_report_datetime.day)
#             if self.offstudy_date < report_date:
#                 raise exception_cls(
#                     'Data exists for this subject with a report datetime '
#                     'AFTER the off study date of {0}. See {1} with '
#                     'report_datetime {2}.'.format(
#                         self.offstudy_date, self.VISIT_MODEL._meta.object_name, max_report_datetime))

    def off_study_visit_exists_or_raise(self):
        subject_identifier = self.get_subject_identifier()
        report_datetime_min = datetime.combine(self.report_datetime, time.min)
        report_datetime_max = datetime.combine(self.report_datetime, time.max)
        try:
            self.VISIT_MODEL.objects.get(
                appointment__registered_subject__subject_identifier=subject_identifier,
                report_datetime__gt=report_datetime_min,
                report_datetime__lt=report_datetime_max,
                reason=OFF_STUDY)
        except self.VISIT_MODEL.DoesNotExist:
            raise OffStudyError('Off study report must be submitted on an off study visit.')

    def delete_future_appointments_on_offstudy(self):
        """Deletes appointments created after the off-study datetime
        if the appointment has no visit report."""
        Appointment = self.VISIT_MODEL.appointment.field.rel.to
        for appointment in Appointment.objects.filter(
                registered_subject=self.registered_subject,
                appt_datetime__gt=self.offstudy_date):
            # only delete appointments that have no visit report
            try:
                self.VISIT_MODEL.objects.get(appointment=appointment)
            except self.VISIT_MODEL.DoesNotExist:
                appointment.delete()

    def get_report_datetime(self):
        return datetime(self.offstudy_date.year,
                        self.offstudy_date.month,
                        self.offstudy_date.day)

    class Meta:
        abstract = True
