from django.db import models


class OffStudyMixin(models.Model):

    OFF_STUDY_MODEL = None

    def is_off_study(self):
        """Returns True if the off-study form exists for this subject, otherwise False.

        Once consented, a subject must be deliberately taken "off study" using a model that
        is a subclass of :class:`off_study.models.BaseOffStudy`."""
        try:
            subject_identifier = self.subject_identifier
        except AttributeError:
            subject_identifier = self.get_subject_identifier()
        try:
            report_datetime = self.report_datetime
        except AttributeError:
            report_datetime = self.get_report_datetime()
        report_date = report_datetime.date()
        return self.OFF_STUDY_MODEL.objects.filter(
            registered_subject__subject_identifier=subject_identifier,
            offstudy_date__lt=report_date).exists()

    class Meta:
        abstract = True
