from django.apps import apps as django_apps
from django.db import models
from django.db.models import Q
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_model.models import BaseUuidModel
from edc_model.validators import datetime_not_future
from edc_protocol.validators import datetime_not_before_study_start
from edc_utils import get_utcnow

from ..choices import SCHEDULE_STATUS
from ..model_mixins import VisitScheduleFieldsModelMixin


class OnScheduleModelError(Exception):
    pass


class SubjectScheduleModelManager(models.Manager):
    def get_by_natural_key(self, subject_identifier, visit_schedule_name, schedule_name):
        return self.get(
            subject_identifier=subject_identifier,
            visit_schedule_name=visit_schedule_name,
            schedule_name=schedule_name,
        )

    def onschedules(self, subject_identifier=None, report_datetime=None):
        """Returns a list of onschedule model instances for this
        subject where the schedule_status would be ON_SCHEDULE
        relative to the report_datetime.
        """
        onschedules = []
        report_datetime = report_datetime or get_utcnow()
        qs = self.filter(
            Q(subject_identifier=subject_identifier),
            Q(onschedule_datetime__lte=report_datetime),
            (
                Q(offschedule_datetime__gte=report_datetime)
                | Q(offschedule_datetime__isnull=True)
            ),
        )
        for obj in qs:
            onschedule_model_cls = django_apps.get_model(obj.onschedule_model)
            onschedules.append(
                onschedule_model_cls.objects.get(subject_identifier=subject_identifier)
            )
        return onschedules


class SubjectScheduleHistory(
    NonUniqueSubjectIdentifierFieldMixin,
    VisitScheduleFieldsModelMixin,
    BaseUuidModel,
):
    onschedule_model = models.CharField(max_length=100)

    offschedule_model = models.CharField(max_length=100)

    onschedule_datetime = models.DateTimeField(
        validators=[datetime_not_before_study_start, datetime_not_future]
    )

    offschedule_datetime = models.DateTimeField(
        validators=[datetime_not_before_study_start, datetime_not_future], null=True
    )

    schedule_status = models.CharField(max_length=15, choices=SCHEDULE_STATUS, null=True)

    objects = SubjectScheduleModelManager()

    def natural_key(self):
        return (
            self.subject_identifier,
            self.visit_schedule_name,
            self.schedule_name,
        )

    class Meta(BaseUuidModel.Meta):
        unique_together = ("subject_identifier", "visit_schedule_name", "schedule_name")
