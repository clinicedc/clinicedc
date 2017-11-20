from django.apps import apps as django_apps
from django.db import models
from django.utils import timezone
from edc_visit_schedule.model_mixins import VisitScheduleMethodsModelMixin


class SubjectOffstudyError(Exception):
    pass


class OffstudyMixin(VisitScheduleMethodsModelMixin, models.Model):

    """A mixin for CRF models to add the ability to determine
    if the subject is off study.
    """

    def save(self, *args, **kwargs):
        self.is_offstudy_or_raise()
        super(OffstudyMixin, self).save(*args, **kwargs)

    @property
    def offstudy_model(self):
        # FIXME: if you get an AttributeError, is self.visit_schedule
        # not going to just raise another. Use the visit schedule methods
        # mixin? If instance is being saved for the first time???
        offstudy_model = None
        try:
            offstudy_model = self.visit.visit_schedule.models.get(
                'offstudy_model')
        except AttributeError as e:
            if 'visit' in str(e):
                try:
                    offstudy_model = self.visit_schedule.offstudy_model
                except AttributeError as e:
                    raise SubjectOffstudyError(str(e))
            else:
                raise SubjectOffstudyError(str(e))
        return django_apps.get_model(*offstudy_model.split('.'))

    def is_offstudy_or_raise(self):
        """Return True if the off-study report exists. """
        try:
            offstudy = self.offstudy_model.objects.get(
                offstudy_datetime__lte=self.report_datetime,
                subject_identifier=self.subject_identifier
            )
            raise SubjectOffstudyError(
                'Participant was reported off study on \'{0}\'. '
                'Data reported after this date'
                ' cannot be captured.'.format(timezone.localtime(
                    offstudy.offstudy_datetime).strftime('%Y-%m-%d')))
        except self.offstudy_model.DoesNotExist:
            offstudy = None
        return offstudy

    class Meta:
        abstract = True
