from django.apps import apps as django_apps
from django.db import models
from django.db.models import Q, UniqueConstraint
from django.utils import timezone

from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_model.models import BaseUuidModel
from edc_model.validators import datetime_not_future
from edc_protocol.validators import datetime_not_before_study_start
from edc_sites.managers import CurrentSiteManager
from edc_sites.model_mixins import SiteModelMixin

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
        report_datetime = report_datetime or timezone.now()
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
    SiteModelMixin,
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

    schedule_status = models.CharField(max_length=15, choices=SCHEDULE_STATUS, default="")

    objects = SubjectScheduleModelManager()

    on_site = CurrentSiteManager()

    def natural_key(self):
        return (
            self.subject_identifier,
            self.visit_schedule_name,
            self.schedule_name,
        )

    @property
    def onschedule_obj(self):
        return self.onschedule_model_cls.objects.get(
            subject_identifier=self.subject_identifier
        )

    @property
    def offschedule_obj(self):
        return self.offschedule_model_cls.objects.get(
            subject_identifier=self.subject_identifier
        )

    @property
    def onschedule_model_cls(self):
        return django_apps.get_model(self.onschedule_model)

    @property
    def offschedule_model_cls(self):
        return django_apps.get_model(self.offschedule_model)

    class Meta(BaseUuidModel.Meta, NonUniqueSubjectIdentifierFieldMixin.Meta):
        constraints = (
            UniqueConstraint(
                fields=["subject_identifier", "visit_schedule_name", "schedule_name"],
                name="%(app_label)s_%(class)s_subject_uniq",
            ),
        )
        indexes = (
            *BaseUuidModel.Meta.indexes,
            *NonUniqueSubjectIdentifierFieldMixin.Meta.indexes,
        )
